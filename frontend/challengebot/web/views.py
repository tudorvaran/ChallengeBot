# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import re

# Create your views here.
import sys
from django.contrib.auth.models import User

from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.template import loader
from django.utils import timezone

from .code_submit import submit_submission, submit_challenge
from .forms import SubmissionForm, ChallengeForm

from .models import Game, Challenge, Job, Submission, Source, LevelGame, LevelingUser


def get_rendered_menu(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    template = loader.get_template(os.path.join('web', 'menu.html'))
    return template.render(context, request)


def games(request):
    games_list = Game.objects.all()
    content_template = loader.get_template(os.path.join('web', 'games.html'))
    content_context = {'games_list': games_list}
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))


def challenges(request):
    challenges_list = Challenge.objects.order_by('-id')
    content_template = loader.get_template(os.path.join('web', 'challenges.html'))
    content_context = {'challenges_list': challenges_list}
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))

def job(request, job_id):
    #challenge_obj = get_object_or_404(Challenge, pk=int(challenge_id))
    log =None
    challenge_objs = Challenge.objects.filter(job_id=job_id)
    if len(challenge_objs) > 0:
        pass
    else:
        submission_obj = Submission.objects.filter(job_id=job_id)[0]
        log = open(submission_obj.job.log_path)
    content_template = loader.get_template(os.path.join('web', 'job.html'))
    rows = []
    for line in log:
        rows.append(line)

    content_context = {'rows': rows}
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))

def game(request, game_id):
    game_obj = get_object_or_404(Game, pk=int(game_id))
    levelgame_obj = LevelGame.objects.filter(game=game_obj).order_by('level')
    content_template = loader.get_template(os.path.join('web', 'game.html'))
    content_context = {'game': game_obj}
    if len(levelgame_obj) > 0:
        content_context['levels'] = levelgame_obj
        if request.user.is_authenticated:
            try:
                content_context['leveluser'] = LevelingUser.objects.get(game=game_obj, user=request.user)
                content_context['xp_reach'] = LevelGame.objects.get(game=game_obj, level=content_context['leveluser'].level).xp_reach
            except:
                pass

    if request.user.is_authenticated:
        content_context['form'] = SubmissionForm
        if Source.objects.filter(user_id=request.user.id, game_id=game_id, selected=1):
            content_context['p1_source'] = Source.objects.get(user_id=request.user.id, game_id=game_id, selected=1)
            content_context['opponents'] = ChallengeForm(game_id=game_id, user_id=request.user.id,
                                                 max_players=game_obj.players_max - 1, min_players=game_obj.players_min - 1)
    template = loader.get_template(os.path.join('web', 'games', game_obj.name + '.html'))
    content_context['game_description'] = template.render({}, request)
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))


def ranking(request, game_id=None, rank_page=None):
    content_template = loader.get_template(os.path.join('web', 'ranking.html'))
    levelgames_list = LevelGame.objects.values('game').distinct().order_by('game')
    games_list = [Game.objects.get(pk=levelgame.values()[0]) for levelgame in levelgames_list]
    rankings_list = []
    position = 1
    if game_id is not None:
        if rank_page is None:
            return redirect('/ranking/' + game_id + '/1')
        rank_page = int(rank_page)
        rankings_list = LevelingUser.objects.filter(game=int(game_id)).order_by('-level', '-xp')
        max_page = len(rankings_list) // 20 + 1
        if rank_page > max_page:
            return redirect('/ranking/' + game_id + '/' + str(max_page))
        if len(rankings_list) > 20:
            min_rank = max(len(rankings_list) - 20 * rank_page, 0)
            max_rank = min(len(rankings_list) - 20 * (rank_page - 1), len(rankings_list))
            position = len(rankings_list) - max_rank + 1
            ranking_list = rankings_list[len(rankings_list) - max_rank: len(rankings_list) - min_rank]
    else:
        rank_page = 1
        max_page = 1
    content_context = {
        'rankings_list': rankings_list,
        'max_page': max_page,
        'rank_page': rank_page,
        'games': games_list,
        'position': position,
        'game_id': game_id
    }
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))


def jobs(request, job_page):
    job_page = int(job_page)
    job_list = Job.objects.order_by('-id')
    challenge_list = Challenge.objects.order_by('-id')
    submission_list = Submission.objects.order_by('-id')
    content_template = loader.get_template(os.path.join('web', 'jobs.html'))
    max_page = len(job_list) // 20 + 1
    if job_page > max_page:
        return redirect('/jobs/' + str(max_page))
    if len(job_list) > 20:
        min_job = max(len(job_list) - 20 * job_page, 0)
        max_job = min(len(job_list) - 20 * (job_page - 1), len(job_list))
        job_list = job_list[len(job_list) - max_job: len(job_list) - min_job]
    filtered_challenge_list = []
    filtered_submission_list = []
    for ch in challenge_list:
        if ch.job in job_list:
            filtered_challenge_list.append(ch)
    for sub in submission_list:
        if sub.job in job_list:
            filtered_submission_list.append(sub)
    content_context = {
        'job_list': job_list,
        'challenge_list': filtered_challenge_list,
        'submission_list': filtered_submission_list,
        'max_page': max_page,
        'job_page': job_page,
    }
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))


def about(request):
    content_template = loader.get_template(os.path.join('web', 'about.html'))
    content_context = {}
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))


def index(request):
    content_template = loader.get_template(os.path.join('web', 'index.html'))
    content_context = {}
    context = {}
    context['menu'] = get_rendered_menu(request)
    context['content'] = [content_template.render(content_context, request)]
    template = loader.get_template(os.path.join('web', 'template.html'))
    return HttpResponse(template.render(context, request))

