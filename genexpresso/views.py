from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from threading import Thread
from .models import Project, Dataset
from .forms import ProjectForm, DatasetForm
from .data_processing import fetch_geo_data, preprocess_geo_data, generate_heatmap, generate_pca, generate_umap
import pandas as pd


dataset_status = {}


def index(request):
    """Home page of the application."""
    return render(request, 'genexpresso/index.html')


@login_required
def projects(request):
    """Display all projects of the logged-in user."""
    projects = Project.objects.filter(owner=request.user).order_by('-date_added')
    return render(request, 'genexpresso/projects.html', {'projects': projects})


@login_required
def project(request, project_id):
    """Display a single project and its datasets."""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        raise Http404("You do not have permission to view this project.")

    datasets = project.dataset_set.order_by('-date_added')
    return render(request, 'genexpresso/project.html', {'project': project, 'datasets': datasets})


@login_required
def new_project(request):
    """Add a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.owner = request.user
            new_project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('genexpresso:projects')
    else:
        form = ProjectForm()

    return render(request, 'genexpresso/new_project.html', {'form': form})


@login_required
def edit_project(request, project_id):
    """Edit an existing project."""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        raise Http404("You do not have permission to edit this project.")

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('genexpresso:projects')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'genexpresso/edit_project.html', {'project': project, 'form': form})


@login_required
def delete_project(request, project_id):
    """Delete a project."""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        raise Http404("You do not have permission to delete this project.")

    project.delete()
    messages.success(request, 'Project deleted successfully!')
    return redirect('genexpresso:projects')


@login_required
def new_dataset(request, project_id):
    """Add a new dataset to a project."""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        raise Http404("You do not have permission to add datasets to this project.")

    if request.method == 'POST':
        form = DatasetForm(request.POST)
        if form.is_valid():
            new_dataset = form.save(commit=False)
            new_dataset.project = project
            new_dataset.save()
            messages.success(request, 'Dataset created successfully!')
            return redirect('genexpresso:project', project_id=project.id)
    else:
        form = DatasetForm()

    return render(request, 'genexpresso/new_dataset.html', {'form': form, 'project': project})


@login_required
def edit_dataset(request, dataset_id):
    """Edit an existing dataset."""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    project = dataset.project

    if project.owner != request.user:
        raise Http404("You do not have permission to edit this dataset.")

    if request.method == 'POST':
        form = DatasetForm(request.POST, instance=dataset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dataset updated successfully!')
            return redirect('genexpresso:project', project_id=project.id)
    else:
        form = DatasetForm(instance=dataset)

    return render(request, 'genexpresso/edit_dataset.html', {'form': form, 'project': project, 'dataset': dataset})


@login_required
def delete_dataset(request, dataset_id):
    """Delete a dataset."""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    project = dataset.project

    if project.owner != request.user:
        raise Http404("You do not have permission to delete this dataset.")

    dataset.delete()
    messages.success(request, 'Dataset deleted successfully!')
    return redirect('genexpresso:project', project_id=project.id)


@login_required
def analyze_dataset(request, dataset_id):
    """Start dataset analysis and redirect to loading page."""
    dataset = get_object_or_404(Dataset, id=dataset_id)

    if dataset.project.owner != request.user:
        raise Http404("You do not have permission to analyze this dataset.")

    if dataset_id not in dataset_status or dataset_status[dataset_id].get("status") not in ["processing", "done"]:
        dataset_status[dataset_id] = {"status": "processing"}

        analysis_thread = Thread(target=perform_analysis, args=(dataset_id,))
        analysis_thread.start()

    return redirect('genexpresso:loading_page', dataset_id=dataset_id)


def perform_analysis(dataset_id):
    """Perform dataset analysis and update status."""
    try:
        dataset = Dataset.objects.get(id=dataset_id)

        print(f"Starting analysis for dataset {dataset_id} (GEO ID: {dataset.geo_id})")

        geo_data, group_labels = fetch_geo_data(dataset.geo_id)

        if geo_data is None or geo_data.empty:
            print(f"Error: GEO dataset {dataset.geo_id} is empty!")
            dataset_status[dataset_id] = {"status": "error"}
            return

        processed_data = preprocess_geo_data(geo_data)

        if processed_data is None or processed_data.empty:
            print(f"Error: Processed dataset {dataset.geo_id} is empty after preprocessing!")
            dataset_status[dataset_id] = {"status": "error"}
            return

        dataset_status[dataset_id] = {
            'processed_data': processed_data, 
            'heatmap': generate_heatmap(processed_data, group_labels),
            'pca': generate_pca(processed_data, group_labels),
            'umap': generate_umap(processed_data, group_labels),
            'status': "done"
        }

        print(f"Success: Dataset {dataset_id} processed successfully!")

    except Exception as e:
        print(f"Error in processing dataset {dataset_id}: {e}")
        dataset_status[dataset_id] = {"status": "error"}

@login_required
def export_processed_data(request, dataset_id):
    """Export the processed dataset as a CSV file."""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    
    if dataset_id not in dataset_status or dataset_status[dataset_id]["status"] != "done":
        messages.error(request, "Data is not ready for export.")
        return redirect('genexpresso:analyze_dataset_results', dataset_id=dataset_id)

    processed_data = dataset_status[dataset_id].get("processed_data")

    if processed_data is None:
        messages.error(request, "No processed data available for export.")
        return redirect('genexpresso:analyze_dataset_results', dataset_id=dataset_id)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="processed_data_{dataset_id}.csv"'
    processed_data.to_csv(response, index=True)

    return response

@login_required
def loading_page(request, dataset_id):
    """Render loading page while waiting for dataset analysis."""
    dataset = get_object_or_404(Dataset, id=dataset_id)
    project = dataset.project

    status = dataset_status.get(dataset_id, {}).get("status", "processing")

    # ✅ Redirect when processing is complete
    if status == "done":
        print(f"Redirecting: Dataset {dataset_id} processing complete, showing visualizations.")
        return redirect('genexpresso:analyze_dataset_results', dataset_id=dataset_id)
    elif status == "error":
        print(f"Redirecting: Dataset {dataset_id} failed.")
        return redirect('genexpresso:project', project_id=project.id)

    return render(request, 'genexpresso/loading_page.html', {
        'dataset_id': dataset_id,
        'project_id': project.id,
        'status': status,  
    })


@login_required
def analyze_dataset_results(request, dataset_id):
    """Display dataset visualizations."""
    dataset = get_object_or_404(Dataset, id=dataset_id)

    if dataset.project.owner != request.user:
        raise Http404("You do not have permission to analyze this dataset.")

    if dataset_status.get(dataset_id, {}).get("status") != "done":
        return redirect('genexpresso:loading_page', dataset_id=dataset_id)
    
    visualizations = {
        'heatmap': dataset_status[dataset_id].get('heatmap'),
        'pca': dataset_status[dataset_id].get('pca'),
        'umap': dataset_status[dataset_id].get('umap'),
    }

    return render(request, 'genexpresso/analyze_dataset.html', {
        'dataset': dataset,
        'visualizations': visualizations
    })


@login_required
def check_status(request, dataset_id):
    """Check the dataset processing status and return JSON response."""
    status = dataset_status.get(dataset_id, {}).get("status", "processing")
    print(f"Check Status: Dataset {dataset_id} → {status}")
    return JsonResponse({"status": status})

def logout_page(request):
    """Log the user out and redirect to the home page."""
    username = request.user.username
    logout(request)
    return render(request,'genexpresso/logout_page.html', {'username': username})


def help_page(request):
    """Guide for user to use the website."""
    return render(request, 'genexpresso/help_page.html')



