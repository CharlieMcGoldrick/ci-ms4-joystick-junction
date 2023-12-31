from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm
from .models import (
    MainThread,
    Comment,
    Upvote,
    Downvote,
    Reply,
    ReplyUpvote,
    ReplyDownvote
)
from django.http import (
    JsonResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest
)
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from datetime import datetime
from .api.api import make_igdb_api_request
from django.db.models import Q, Count
import json


def home(request):
    """
    Home view that displays the main threads, popular threads, and new
    threads.
    """
    main_threads = MainThread.objects.filter(status=1)
    popular_threads = MainThread.objects.filter(status=1).annotate(
        num_comments=Count('comments')).order_by('-num_comments')[:5]
    new_threads = MainThread.objects.filter(status=1).order_by(
        '-created_date')[:5]
    return render(request, 'index.html', {
        'main_threads': main_threads,
        'new_threads': new_threads,
        'popular_threads': popular_threads
    })


def homepage_search_threads(request):
    """
    View for searching threads from the homepage.
    """
    query = request.GET.get('search')
    results = MainThread.objects.filter(
        Q(name__icontains=query),
        status=1  # Only include published threads
    )[:5]  # Limit to top 5 results

    if results.exists():
        results_data = []
        for result in results:
            result_data = {
                'name': result.name,
                'url': reverse('main_thread_detail', args=[result.game_id]),
            }
            results_data.append(result_data)
        return JsonResponse({'results': results_data})
    else:
        return JsonResponse({'no_results': True})


def main_thread_detail(request, game_id):
    """
    View for displaying the details of a main thread.
    """
    main_thread = MainThread.objects.get(game_id=game_id)

    # Convert the data into a clean format
    main_thread.genres = ', '.join(
        [genre['name'] for genre in json.loads(main_thread.genres)])
    main_thread.platforms = ', '.join(
        [platform['name'] for platform in json.loads(main_thread.platforms)])
    main_thread.involved_companies = ', '.join(
        [company['company']['name'] for company in json.loads(
            main_thread.involved_companies)])
    main_thread.game_engines = ', '.join(
        [engine['name'] for engine in json.loads(main_thread.game_engines)])

    # Round down the aggregated rating
    main_thread.aggregated_rating = round(main_thread.aggregated_rating)

    return render(request, 'main_thread_detail.html', {
        'main_thread': main_thread
    })


@login_required
def post_comment(request, game_id):
    """
    View for posting a comment to a main thread.
    """
    # Ensure the request is a POST request
    if request.method == 'POST':
        # Get the MainThread instance
        mainthread = get_object_or_404(MainThread, game_id=game_id)

        # Get the comment text from the form data
        text = request.POST.get('text')

        # Create a new Comment instance
        Comment.objects.create(
            game_id=mainthread,
            user=request.user,
            text=text
        )

        # Redirect to the main_thread_detail page
        return redirect('main_thread_detail', game_id=game_id)

    # If the request is not a POST request, return an error response
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def reply_to_comment(request, comment_id):
    """
    View for replying to a comment.
    """
    if request.method == 'POST':
        parent_comment = get_object_or_404(Comment, id=comment_id)
        text = request.POST.get('text')
        reply = Reply.objects.create(
            comment=parent_comment, user=request.user, text=text)

        # Redirect to the main_thread_detail page
        return redirect('main_thread_detail', game_id=reply.comment.game_id.game_id)
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def upvote_comment(request, comment_id):
    """
    View for upvoting a comment.
    """
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        Upvote.objects.create(user=request.user, comment=comment)

        # Redirect to the main_thread_detail page
        return redirect(
            'main_thread_detail',
            game_id=comment.game_id.game_id
        )
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def downvote_comment(request, comment_id):
    """
    View for downvoting a comment.
    """
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        Downvote.objects.create(user=request.user, comment=comment)

        # Redirect to the main_thread_detail page
        return redirect(
            'main_thread_detail',
            game_id=comment.game_id.game_id
        )
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def upvote_reply(request, reply_id):
    """
    View for upvoting a reply.
    """
    if request.method == 'POST':
        reply = get_object_or_404(Reply, id=reply_id)
        ReplyUpvote.objects.create(user=request.user, reply=reply)

        # Redirect to the main_thread_detail page
        return redirect(
            'main_thread_detail',
            game_id=reply.comment.game_id.game_id
        )
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def downvote_reply(request, reply_id):
    """
    View for downvoting a reply.
    """
    if request.method == 'POST':
        reply = get_object_or_404(Reply, id=reply_id)
        ReplyDownvote.objects.create(user=request.user, reply=reply)

        # Redirect to the main_thread_detail page
        return redirect(
            'main_thread_detail',
            game_id=reply.comment.game_id.game_id
        )
    else:
        return HttpResponseBadRequest('Invalid request')


def make_main_thread_search_request(query):
    """
    Helper function to make a search request for main threads.
    """
    endpoint = 'games'
    query_body = (
        f'fields name,genres.name,platforms.name,summary,'
        f'involved_companies.company.name,game_engines.name,'
        f'aggregated_rating; where (category = 0 | category = 10) & '
        f'version_title = null; search "{query}"; limit 10;'
    )
    return make_igdb_api_request(endpoint, query_body)


def search_games_for_main_thread(request):
    """
    View for searching games for main threads.
    """
    search_query = request.GET.get('query', '')
    results = make_main_thread_search_request(search_query)
    return JsonResponse(results, safe=False)


def create_game_main_thread(request, game_id):
    """
    View for creating a game main thread.
    """
    data = json.loads(request.body)
    game_name = data.get('game_name')
    genres = json.loads(data.get('genres', '[]'))
    platforms = json.loads(data.get('platforms', '[]'))
    summary = data.get('summary')
    involved_companies = json.loads(data.get('involved_companies', '[]'))
    game_engines = json.loads(data.get('game_engines', '[]'))
    aggregated_rating = data.get('aggregated_rating')
    if MainThread.objects.filter(game_id=game_id).exists():
        return JsonResponse(
            {'error': 'A thread for this game already exists.'},
            status=400
        )

    try:
        game = MainThread(
            name=game_name,
            game_id=game_id,
            summary=summary,
            aggregated_rating=aggregated_rating
        )
        game.set_genres(genres)
        game.set_platforms(platforms)
        game.set_involved_companies(involved_companies)
        game.set_game_engines(game_engines)
        game.save()
        return JsonResponse({'success': 'Thread created successfully.'})
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)


def search_created_main_threads(request):
    """
    View for searching created main threads.
    """
    search = request.GET.get('search', '')
    threads = MainThread.objects.filter(name__icontains=search).values()
    thread_list = list(threads)
    return JsonResponse(thread_list, safe=False)


@require_POST
def update_and_publish_thread(request):
    """
    View for updating and publishing a thread.
    This view requires a POST request.
    """
    try:
        game_id = request.POST.get('game_id')
        visibility_states = json.loads(request.POST.get('visibility_states'))

        thread = MainThread.objects.get(game_id=game_id)

        # Update visibility states for each field
        for field, is_visible in visibility_states.items():
            setattr(thread, f'{field}_visible', is_visible)

        # Set thread status to published
        thread.status = 1
        thread.save()

        return JsonResponse(
            {'status': 'This thread was succesfully updated and published'}
        )
    except MainThread.DoesNotExist:
        return JsonResponse({'error': 'MainThread not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


@require_POST
def update_and_unpublish_thread(request):
    """
    View for updating and unpublishing a thread.
    This view requires a POST request.
    """
    try:
        game_id = request.POST.get('game_id')
        visibility_states = json.loads(request.POST.get('visibility_states'))

        thread = MainThread.objects.get(game_id=game_id)

        # Update visibility states for each field
        for field, is_visible in visibility_states.items():
            setattr(thread, f'{field}_visible', is_visible)

        # Set thread status to unpublished
        thread.status = 0
        thread.save()

        return JsonResponse(
            {'status': 'This thread was succesfully updated and unpublished'}
        )
    except MainThread.DoesNotExist:
        return JsonResponse({'error': 'MainThread not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


@require_POST
def delete_a_main_thread(request):
    """
    View for deleting a main thread.
    This view requires a POST request.
    """
    try:
        game_id = request.POST.get('game_id')

        thread = MainThread.objects.get(game_id=game_id)
        thread.delete()

        return JsonResponse({'status': 'success'})
    except MainThread.DoesNotExist:
        return JsonResponse({'error': 'MainThread not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)


def account_management(request):
    """
    View for managing user accounts.
    """
    results = None
    form_submitted = False
    return render(request, 'account_management.html')


def signup_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        signup_form = SignupForm(data)

        if signup_form.is_valid():
            user = signup_form.save()
            group, created = Group.objects.get_or_create(name='BasicUser')
            group.user_set.add(user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': signup_form.errors}, status=400)

    else:
        signup_form = SignupForm()

    return render(request, 'signup.html', {'signup_form': signup_form})


def check_username_email(request):
    data = json.loads(request.body)
    username = data.get('username')
    email = data.get('email')

    data = {
        'username_taken': User.objects.filter(username=username).exists(),
        'email_taken': User.objects.filter(email=email).exists()
    }

    return JsonResponse(data)


class login_view(LoginView):
    """
    View for handling user login.
    Inherits from Django's built-in LoginView.
    """

    def form_valid(self, form):
        """
        Overridden method from LoginView.
        Called when the login form is valid.

        Sets a test cookie and logs the user in.
        Returns a JSON response indicating success.
        """
        self.request.session.set_test_cookie()
        auth_login(self.request, form.get_user())
        return JsonResponse({
            'status': 'success',
            'message': 'Login successful! Redirecting to home page...'
        })

    def form_invalid(self, form):
        """
        Overridden method from LoginView.
        Called when the login form is invalid.

        Returns a JSON response indicating an error.
        """
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid username or password.'
        }, status=400)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def promote_to_admin(request):
    """
    View for promoting a user to admin.
    This view requires the user to be logged in and be a superuser.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(
            username=username,
            groups__name='BasicUser'
        ).first()
        if user:
            user.is_staff = True
            user.save()
            return redirect('account_management')
    return redirect('account_management')


def logout_view(request):
    """
    View for logging out a user.
    """
    logout(request)
    return redirect('home')


def custom_error_404(request, exception):
    """
    Custom view for handling 404 errors.
    """
    return render(request, '404.html', {}, status=404)


def custom_error_500(request):
    """
    Custom view for handling 500 errors.
    """
    return render(request, '500.html', {}, status=500)


def custom_error_403(request, exception):
    """
    Custom view for handling 403 errors.
    """
    return render(request, '403.html', {}, status=403)
