from django.shortcuts import render


def view_index(request):
    '''Main page.'''
    return render(request, 'index.html')


def view_boxes(request):
    '''Boxes page.'''
    return render(request, 'boxes.html')
