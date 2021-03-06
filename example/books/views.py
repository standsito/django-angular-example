
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.db import connection

from django.core.cache import cache

from forms import AuthorForm, BookForm, PublisherForm
from models import Author, Book, Publisher

import logging
logger = logging.getLogger(__name__)
#logger = logging.getLogger('djplogger')

@require_GET
def show_template(request, template_name):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))



@require_http_methods(['GET', 'POST'])
def list_and_add_view(request, template_name, model, formclass):
    if request.method == 'GET':
        form = formclass()
    else:
        form = formclass(request.POST)
    
    logger.info('Created form')
    
    if not form.is_valid() or request.method == 'GET':
        return render_to_response(template_name,
                                  {'form': form,
                                   'object_list': model.objects.all()},
                                  context_instance=RequestContext(request))
    else:
        logger.info('Saving new item')
        newitem = form.save()
        logger.info('New item saved')
        
        messages.success(request, "Item %s was added" % newitem)
        return HttpResponseRedirect(request.build_absolute_uri())



@require_http_methods(['GET', 'POST'])
def book_view(request):
    if request.method == 'GET':
        form = BookForm()
    else:
        form = BookForm(request.POST)
    
    logger.info('Retrieving books...')
    
    """
    WARING: this line will technically work, but is horribly sub-optimal.
    djangoperformance.com will make you aware of that sub-optimality by telling
    you how many queries are being generated for each view, and what those queries are
    """
#    books = Book.objects.all()
    
    """
    this is a simple solution to reduce the number of queries issued to the database.
    this should not be considered a recipe for optimizing all applications, and is only
    used here to illustrate expected use case of djangoperformance.com
    (you may, for example, want to use a custom model manager if you're doing something complicated
    in your application)
    """
    books = Book.objects.select_related('publisher').all().prefetch_related('authors')
    
    logger.info('Found %d books' % books.count())
    
    if not form.is_valid() or request.method == 'GET':
        return render_to_response('books.html',
                                  {'form': form,
                                   'object_list': books},
                                  context_instance=RequestContext(request))
    else:
        logger.info('Saving new book')
        newitem = form.save()
        logger.info('Saved new book')
        
        messages.success(request, "Book %s was added" % newitem)
        return HttpResponseRedirect(request.build_absolute_uri())


