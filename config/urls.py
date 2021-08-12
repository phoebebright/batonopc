

#from registration.backends.simple.views import RegistrationView
#from web.forms import CustomUserForm


from django.urls import register_converter
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from material.frontend import urls as frontend_urls
from qr_code import urls as qr_code_urls
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from obstacles.views import ScoreObstacles
from helpdesk.api import *
# from todo.api import *

from web.api import *
from web.api_ro import CompetitionViewseRO, EntryViewsetRO
from web.api_enter import EntryEnterViewset, AddorUpdateEntry
from web.api_money import *
from web.api_keycloak import *
from web.autocompletes import (EventAutocomplete, HorseAutocomplete,
                               JudgesAutocomplete, OrganisersAutocomplete,
                               RidersAutocomplete, ScorersAutocomplete,
                               TestSheetAutocomplete, WritersAutocomplete)
from web.importexport import (CreateEventReport,
                              EventResultsExport, EventEntriesExport,
                              event_scores_export, event_starttimes_export,
                              issuer_testsheets_xls, event_starttimes_export_xls)
from web.scrapers import (process_rider_results, scrape_di_results,
                          scrape_ei_events, scrape_ei_results)
from web.views import *
from tools.ref import TestRefConverter, EventRefConverter, SheetRefConverter, CompetitionRefConverter, \
    PersonRefConverter, EntryRefConverter, OrderRefConverter, RoleRefConverter
from integrations.views import UploadEntriesView, UploadCompetitionsView

challenge_dir = os.path.join(settings.BASE_DIR,".well-known/acme-challenge")

admin.autodiscover()



register_converter(TestRefConverter, 'testref')
register_converter(EventRefConverter, 'event_ref')
register_converter(SheetRefConverter, 'sheetref')
register_converter(CompetitionRefConverter, 'compref')
register_converter(PersonRefConverter, 'personref')
register_converter(EntryRefConverter, 'entryref')
register_converter(OrderRefConverter, 'orderref')
register_converter(RoleRefConverter, 'roleref')


router = routers.DefaultRouter()
router_ro = routers.DefaultRouter()  # readonly apis
router_enter = routers.DefaultRouter()   # related to entry and review of entries

router.register(r'arenas', ArenaViewset)
router.register(r'break_slots', SlotBreakViewset,"breakslot-api")
router.register(r'competition_slots', SlotCompetitionViewset)

router.register(r'competitions', CompetitionViewset)

router.register(r'competition_judge', CompetitionJudgeViewset)
router.register(r'sync_user', SyncUser)
router.register(r'entries', EntryViewset, basename="entries")
# router.register(r'entry_list', EntryListViewsetRO, basename="entry-list-ro")  #RO
router.register(r'entry_slots', SlotEntryViewset)
router.register(r'event_arenas', EventArenaViewset)
router.register(r'event_judges', EventJudgeViewset)


router.register(r'events/onnow', EventsOnNowViewset)
router.register(r'events/past', EventsPastViewset)
router.register(r'events/future', EventsFutureViewset)

router.register(r'events', EventViewset)  # general list
router.register(r'event', OrganiserEventViewset)  # specific item - organisers only




router.register(r'history', ScoreSheetHistoryViewSet)
router.register(r'horses', HorseViewSet)
router.register(r'issuers', IssuerViewSet)
router.register(r'judges', JudgeViewSet)
router.register(r'my_events', MyEventsViewset, basename="myevents")
router.register(r'my_horses', MyHorseViewSet, basename="myhorses")
router.register(r'my_riders', MyRiderViewSet, basename="myriders")
router.register(r'my_scoresheets', MyScoreSheetsView)
router.register(r'news', NewsViewSet)
router.register(r'results', ResultsViewset)
router.register(r'riders', RiderViewSet)
router.register(r'schedule', ScheduleViewset)
router.register(r'scoring', ScoringViewSet) # a set of scores - one will be made master
router.register(r'scores', ScoresViewSet)  # score for a single movement
router.register(r'scoresheet', ScoreSheetViewSet)
router.register(r'incomplete_score', ScoreSheetIncompleteViewSet, basename="scoresheets-edit")
router.register(r'scoresheets', ScoreSheetListViewSet, basename="scoresheets-list")
router.register(r'sheetimage', SheetImageViewSet)

router.register(r'slots', SlotViewset,"slot-api")  #NOT USED
router.register(r'submission', SubmissionViewSet)
router.register(r'submission_from_tinycloud', SubmissionFromTinyCloud)


router.register(r'testsheetlinks', TestLinksViewSet)  # readonly live

# router.register(r'testsheet', TestSheetViewSet)  # read/write all
router.register(r'venues', VenueViewSet)
router.register(r'members', MemberViewSet)


#helpdesk
router.register(r'kbitem', KBItemViewSet)
router.register(r'ticket', TicketViewSet)


router_ro.register(r'competitions', CompetitionViewseRO, basename="competitionsRO")
router_ro.register(r'competition_judges', CompetitionJudgeViewsetRO, basename="competitionjudgeRO")
router_ro.register(r'entries', EntryViewsetRO, basename="entries-ro")
router_ro.register(r'testsheets', TestsViewSet, basename="testsheets-ro")
router_ro.register(r'exercise', ExerciseViewset, basename="exercises-ro")  # list of movements in a test
router_ro.register(r'eventtype', EventTypeViewset, basename="eventtype-ro")
router_ro.register(r'competitiontype', CompetitionTypeViewset, basename="competitiontype-ro")

router_enter.register(r'entries', EntryEnterViewset, basename="entries-enter")



# import pprint
# pprint.pprint(router.get_urls())

def has_role_manager(user):
    if user and user.is_authenticated:
        return user.is_superuser or user.is_manager
    else:
        return False

def has_role_administrator(user):
    if user and user.is_authenticated:
        return user.is_superuser or user.is_administrator
    else:
        return False

def has_role_scorer(user):
    if user and user.is_authenticated:
        return user.is_scorer
    else:
        return False

def is_anon(user):
    return user and not user.is_authenticated

def is_authenticated(user):
    return user and user.is_authenticated



# api

api_urlpatterns = [
    #path('api/v2/score/', quick_save_score, name="quick_save_score"),
    path('api/v2/', include(router.urls)),
    path('api/g1/', include(router_ro.urls)),
    path('api/e1/', include(router_enter.urls)),

    path('api/e1/add_or_update_entry/<event_ref:event_ref>/', AddorUpdateEntry.as_view(), name="add_or_update_entry"),

    path('api/v2/event_entries/<event_ref:event_ref>/', EntryListViewsetRO.as_view({'get': 'list'}),
         name="event_entries_list"),


    path('api/v2/add2calclog/', Add2CalcLog.as_view(), name="add2calclog"),
    path('api/v2/can_write4event/', UserCanWrite4Event.as_view(), name="can_write_check"),
    path('api/v2/change_pw/', ChangePassword.as_view(), name="change_pw"),
    path('api/v2/check/', last_update_check, name="last_update_check"),

    path('api/v2/check_activation/', CheckActivation.as_view(), name="check_activation"),
    path('api/v2/connect_image_to_scoresheet/', connect_image_to_scoresheet, name="connect_image_to_scoresheet"),
    path('api/v2/entries4testsheet/', EntriesByTestsheet.as_view(), name="entries4testsheet"),

    path('api/v2/event_entries_by_time/', EventEntriesByTime.as_view(), name="event_entries_by_time"),   # deprecated use event_entries

    path('api/v2/event_entry_summary/', EventEntrySummary.as_view(), name="event_entry_summary"),
    path('api/v2/event_team/', EventTeamViewset.as_view(), name="event_team_api"),
    path('api/v2/event_team/accept_invite/', EventTeamAcceptInvite.as_view(), name="event_team_accept_invite"),
    path('api/v2/event_team/reject_invite/', EventTeamRejectInvite.as_view(), name="event_team_reject_invite"),
    path('api/v2/event_team/resend_invite/', EventTeamResendInvite.as_view(), name="event_team_resend_invite"),
    path('api/v2/get_new_ref/', new_ref, name="get_new_ref"),
    path('api/v2/getpin/<event_ref:event_ref>/', GetPin.as_view(), name="getpin"),
    path('api/v2/getset_user_mode/', getset_user_mode, name="getset_user_mode"),
    path('api/v2/horses_at_event/<event_ref:event_ref>/', horses_at_event, name="horses_at_event"),
    path('api/v2/import_competition/', CompetitionImport.as_view(), name="import_competition"),
    path('api/v2/import_entries/', EntryImport.as_view(), name="import_entry"),
    path('api/v2/judge_pool/', JudgePool.as_view(), name="event-judge-pool"), #deprecated

    # path('api/v2/event_judges/<roleref:role_ref>/', EventJudgeViewset.as_view(), name="event-judge-lookup"),

    path('api/v2/judges_at_event/<event_ref:event_ref>/', judges_at_event, name="judges_at_event"),
    path('api/v2/last_ref_data_update/', last_ref_data_update, name="last_ref_data_update"),
    path('api/v2/manual_scores/<event_ref:event_ref>/', ManualScores.as_view(), name="manual_scores"),
    path('api/v2/marks_analysis/', marks_analysis, name="marks_analysis"),
    path('api/v2/marks_csv/<event_ref:event_ref>/', marks_csv, name="marks_csv"),
    path('api/v2/my_entered_tally/', my_entered_tally, name="my_entered_tally"),
    path('api/v2/myentries/', MyEntries.as_view(), name="myentries"),
    path('api/v2/publish_schedule/', publish_schedule, name="publish_schedule"),
    path('api/v2/redo_entry/', RedoEntry.as_view(), name="redo_entry"),
    path('api/v2/reissuepin/<event_ref:event_ref>/', ReissuePin.as_view(), name="reissue-pin"),
    path('api/v2/resend_activation/', resend_activation, name="resend_activation"),
    path('api/v2/event_results/<event_ref:event_ref>/', EventResultsAPI.as_view(), name="event_results"),
    path('api/v2/restart_schedule/', restart_schedule, name="restart_schedule"),
    path('api/v2/riders_at_event/<event_ref:event_ref>/', riders_at_event, name="riders_at_event"),
    path('api/v2/riding_at_event/<event_ref:event_ref>/<str:rider_name>/', riding_at_event, name="riding_at_event"),
    path('api/v2/rotate_image/', rotate_image, name="rotate_image"),
    path('api/v2/save_calculation/', save_calculation, name="save_calculation"),
    path('api/v2/save_competition_slots/', save_competition_slots, name="save_competition_slots"),
    path('api/v2/save_entry_slots/', save_entry_slots, name="save_entry_slots"),
    path('api/v2/scan/', scan, name="scan"),
    path('api/v2/scoresheet_csv/<event_ref:event_ref>/', scoresheet_csv, name="scoresheet_csv"),

    path('api/v2/scorings_by_test/<testref:testsheet_ref>/', scorings_by_test, name="scorings_by_test"),
    path('api/v2/signupin/', MobileSignupin.as_view(), name="mobile_signupin"),
    path('api/v2/subscribe_now/', subscribe_now, name="subscribe_now"),
    path('api/v2/testsheet_live/', toggle_testsheet_live_status, name="toggle-testsheet-status"),
    path('api/v2/testsheetq/<testref:testref>/bump_quality/', bump_testsheet, name="bump_testsheet"),
    path('api/v2/toggle_role/<personref:personref>/', toggle_role, name="toggle_role"),
    path('api/v2/toggle_tag_for_deletion/', toggle_tag_for_deletion, name="toggle_tag_for_deletion"),

    path('api/v2/unsubscribe_now/', unsubscribe_now, name="unsubscribe_now"),
    path('api/v2/update_schedule/', update_schedule, name="update_schedule"),
    path('api/v2/upload_scoresheet/', ScoreSheetUploader.as_view(), name="upload-scoresheet"),
    path('api/v2/userprofile/<str:ref>/', UserProfileUpdate.as_view(), name="userprofile_update"),
    path('api/v2/validate_scoresheet/<event_ref:event_ref>/<sheetref:sheetref>/<str:access>/', ValidateSheetref.as_view(), name="validate_scoresheet"),
    path('api/v2/writer4event/', writer4event, name="writer4event"),


    path('api/v2/judge_stats/<compref:comp_ref>/', CompJudgeStatus.as_view(), name="comp_judge_stats"),

    # required as uuid seems to break the auto routing of the ViewSet
    path('api/v2/submission/<uuid:pk>/update_timing/', SubmissionViewSet.as_view({'patch': 'partial_update'}), name="update_submission_timing"),

    # path('api/v2/todo/<event_ref:event_ref>/', TodoViewSet.as_view({'get': 'list', 'post': 'create'}), name="todos"),
    # path('api/v2/todo/<event_ref:event_ref>/<str:group>/', TodoViewSet.as_view({'patch': 'partial_update'}), name="todo-update"),


    # money
    path('api/v2/create_checkout_session/', create_checkout_session, name="create-checkout-session"),
    path('api/v2/pay_order/<orderref:orderref>/', PayOrder.as_view(), name='pay-order'),
    path('pay/<str:status>/', StripePaymentComplete.as_view(), name='payment_complete'),
    # path('charge/', login_required(Charge.as_view()), name='charge'),
    path('fromstripe/', stripe_endpoint, name='stripe_endpoint'),  # TODO: block all but stripe
    path('order_paid/', stripe_endpoint, name='stripe_endpoint'),  # TODO: block all but stripe

    #helpdesk
    path('api/v2/open_issues/<str:element>/', open_issues, name="open_issues"),
]

#NOTE: urls are organised in these groups to make it easy to test them in test_urls.py
library_urlpatterns = [
    # these won't be tested

    # libraries etc.
    #path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path('admin/doc/',include('django.contrib.admindocs.urls')),
    path('apidocs/', include_docs_urls(title='Skorie API', public=False)),
    path('helpdesk/', include('helpdesk.urls', namespace='helpdesk')),

    #path('accounts/', include('allauth.urls'))
    path('js_error_hook/', include('django_js_error_hook.urls')),
    path('invitations/', include('invitations.urls', namespace='invitations')),
    path('invitations/accept/<str:key>/', AcceptCustomInvite.as_view(), name='accept-custom-invite'),
    path('admin/', admin.site.urls),
]

# no login required for these urls
nologin_urlpatterns = [

    # path('signinup/', signinup, name='signinup'),
    path('account/', include('django.contrib.auth.urls')),
    path('keycloak/', include('django_keycloak.urls')),
    path('login/', login_redirect, name='login'),
    path('signup/', signup_redirect, name='signup'),
    path('logout', logout, name="logout"),
    path('logout/', logout, name="logoutb"),

    # path('', include('social_django.urls')),

    path('contact/', ContactView.as_view(), name='contact'),
    path('missing_test/', ContactMissingTest.as_view(), name='contact-missing'),
    path('faq/', TemplateView.as_view(template_name='about/faq.html'), name="faq"),
    path('badpin/', TemplateView.as_view(template_name='bad_pin.html'), name="bad-pin"),

    path('whatson/', EventWhatsOn.as_view(), name="whatson"),
    path('event_search/<str:filter>/', EventSearch.as_view(), name="event-search-filter"),
    path('event_search/', EventSearch.as_view(), name="event_search"),

    path('free/', TemplateView.as_view(template_name='free.html'), name="free"),
    path('qr/', TemplateView.as_view(template_name='qr_link.html'), name="qr"),
    path('privacy/', TemplateView.as_view(template_name='privacy_policy.html'), name="privacy"),
    path('cookies/', TemplateView.as_view(template_name='cookies.html'), name="cookies"),
    path('about/', TemplateView.as_view(template_name='about/faq.html'), name="about"),
    path('roadmap/', TemplateView.as_view(template_name='roadmap.html'), name="roadmap"),
    path('intro/', TemplateView.as_view(template_name='intro.html'), name="intro"),
    path('help/viz/', TemplateView.as_view(template_name='help/analysis.html'), name="help_viz"),
    path('viz_my_score/', VizMyScore.as_view(), name="viz_my_score"),
    path('sheet_noauth/<sheetref:sheetref>/', SheetNoAuth.as_view(), name="sheet_noauth"),

    # to be replaced with api upload with proper permissions
    re_path(r'^api/chunked_upload/?$',
            UploadFile.as_view(), name='api_chunked_upload'),
    re_path(r'^api/chunked_upload_complete/?$',
            UploadCompleteView.as_view(),
            name='api_chunked_upload_complete'),

    re_path(r'^api/upload/entries/?$',
            UploadEntries.as_view(), name='api_upload_entries'),
    re_path(r'^api/upload/entries/complete/?$',
            UploadEntriesComplete.as_view(),
            name='api_upload_entries_complete'),

    re_path(r'^api/upload/competitions/?$',
            UploadCompetitions.as_view(), name='api_upload_competitions'),
    re_path(r'^api/upload/competitions/complete/?$',
            UploadCompetitionsComplete.as_view(),
            name='api_upload_competitions_complete'),

    # go straight to login screen
    # path('account/reset/done/', auth_views.LoginView.as_view(), name='password_reset_complete'),
    #
    #
    # path('account_signup/', account_signup, name='account_signup'),
    # path('resignup/',  TemplateView.as_view(template_name="registration/resignup.html"), name='resignup'),
    # path('accept/<str:pin>/', account_signup_with_pin, name='account_signup_with_pin'),
    #
    # path('password_set/', PasswordSetView.as_view(), name='password_set'),

    # path('signup/', Signup.as_view(), name="signup"),
    # path('signup_thanks/', TemplateView.as_view(template_name="registration/signup_thanks.html"),
    #      name="signup_thanks"),
    # path('confirm/<int:activ_code>/', confirm_signup, name="confirm_signup"),
    # path('signup_done/', TemplateView.as_view(template_name="registration/signup_done.html"), name="signup_done"),

    path('what_next/', WhatNext.as_view(), name="what-next"),  # responds differently if logged in or not

    path('tryjudging/<event_ref:event_ref>/', TryJudging.as_view(), name='try-judging'),
    path('enter/<event_ref:event_ref>/<str:mode>/', EnterOnline.as_view(), name='enter-online-with-mode'),
    path('enter/<event_ref:event_ref>/', EnterOnline.as_view(), name='enter-online'),
    path('enter/<event_ref:event_ref>/video/', UploadVideo.as_view(), name='enter-video'),
    path('enter/<event_ref:event_ref>/video/<entryref:entryref>/', UploadVideo.as_view(), name='enter-video'),
    path('share_enter/<event_ref:event_ref>/', ShareEnterOnline.as_view(), name='share-enter-online'),
]


login_required_urlpatterns = [
    path('registeriofh/', RegisterIofH.as_view(), name="registeriofh"),
    path('send_test_email/', send_test_email, name="send_test_email"),
    path('profile/', UserProfileView.as_view(), name='user_profile'),

    # saving scoresheets
    path('show_and_save/', login_required(ShowAndSave.as_view()), name="show_and_save_no_ref"),
    path('show_and_save/<str:ref>/', login_required(ShowAndSave.as_view()), name="show_and_save"),

    # these options look for user to select event first
    path('add_scoresheet/', login_required(AddScoresheet.as_view()), name="add_scoresheet"),
    path('add_scoresheet/<event_ref:event_ref>/', login_required(AddScoresheet.as_view()), name="add_scoresheet"),
    path('add_scoresheet/<entryref:entryref>/', login_required(AddScoresheet.as_view()), name="add_scoresheet"),

    path('sheet_redirect/<sheetref:ref>/', login_required(SheetRedirect.as_view()), name="sheet_redirect"),

    path('scoresheet/<int:pk>/', login_required(ScoreSheetView.as_view()), name="scoresheet_pk"),
    path('scoresheet/<sheetref:ref>/', login_required(ScoreSheetView.as_view()), name="scoresheet"),
    path('sheetimages/<sheetref:sheetref>/', login_required(SheetImageDetails.as_view()), name="sheetimages"),
    path('process_img/<sheetref:sheetref>/', login_required(process_scoresheet_image), name="process_img"),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    #path('class/<compref:compref>/', class_detail, name="class"),   # unused?

    path('scores/<str:score_id>/', scores, name="scores"),
    path('scoresx/<int:compid>/<str:entryid>/', ScoresX.as_view(), name="scoresx-entry"),  #deprecated - use entryref
    path('scoresx/<entryref:entryref>/', ScoresX.as_view(), name="scoresx-entry"),
    path('scoresx/<compref:compref>/<str:entryid>/', ScoresX.as_view(), name="scoresx-entry"),
    path('scoresx/<compref:compref>/', ScoresX.as_view(), name="scoresx"),
    path('scoresx/<int:compid>/', ScoresX.as_view(), name="scoresx"),

    path('rankings/<int:id>/', rankings, name="rankings-class"),

    path('camera/sheet/<sheetref:sheetref>/', camera, name="camera-sheet"),
    path('addimage/sheet/<sheetref:sheetref>/', login_required(AddImage.as_view()), name="camera-addimage-sheet"),
    path('camera/<int:eventid>/<int:competitionid>/<int:entryid>/', camera, name="camera-entry"),
    path('camera/<str:eventid>/<str:competitionid>/', camera, name="camera"),

]

event_urlpatterns_login = [
    path('camera/<event_ref:event_ref>/', camera, name="camera"),
    path('camera/', camera, name="camera-noevent"),

    #TODO: test putting $ at end of url pattern - should not be anything after
    path('calculator/test/<int:testid>/', Calculator.as_view(), name="calculator-test"),  #deprecated - use testref
    path('calculator/test/<testref:testref>/', Calculator.as_view(), name="calculator-testref"),
    path('calculator/sheet/<sheetref:sheetref>/',  Calculator.as_view(), name="calculator-ref"),
    path('calculator/entry/<str:entryid>/',  Calculator.as_view(), name="calculator-e"),
    path('calculator/competition/<str:competitionref>/',  Calculator.as_view(), name="calculator-c"),

    path('mycalculator/test/<testref:testref>/', Calculator.as_view(), {'mode': "mycalc"}, name="mycalculator-ref"),
    path('mycalculator/sheet/<sheetref:sheetref>/', Calculator.as_view(), {'mode': "mycalc"}, name="mycalculator-sheet"),
    path('mycalculator/', Calculator.as_view(), {'mode': "mycalc"}, name="mycalculator"),
    path('calculator/',  Calculator.as_view(), {'mode': "simple"}, name="calculator"),
    path('calculator/<str:scenario>/',  Calculator.as_view(), {'mode': "simple"}, name="calculator-scenario"),
    path('calculator/<str:scenario>/<testref:testref>/',  Calculator.as_view(), {'mode': "simple"}, name="calculator-scenario-testref"),
    path('calculator/<str:scenario>/<int:id>/',  Calculator.as_view(), {'mode': "simple"}, name="calculator-scenario-id"),

    path('shape_entry.html', login_required(TemplateView.as_view(template_name='shape_entry.html')), name="shape"),

]

event_urlpatterns_organiser = [
    # path('upgrade/',  upgrade, name="upgrade"),

    path('scatter.html/', login_required(TemplateView.as_view(template_name='scatter.html')), name="scatter"),

    path('contact-thanks/', TemplateView.as_view(template_name='contact_thanks.html'), name="contact-thanks"),

    path('settings/', TemplateView.as_view(template_name='settings.html'), name="settings"),
    path('help/', TemplateView.as_view(template_name='help.html'), name="help"),

    path('signup/event/<event_ref:event_ref>/', QuickSignup.as_view(), name="event_signup"),
    path('signup_as_rider/', SignupAsRiderView.as_view(), name="signup_as_rider"),
    path('subscribe_only/', SubscribeView.as_view(), name="subscribe_only"),
    path('unsubscribe_only/', unsubscribe_only, name="unsubscribe_only"),
    path('subscribe_thanks/', TemplateView.as_view(template_name="registration/thanks.html"), name="subscribe_thanks"),


    # path('preview123/', TemplateView.as_view(template_name="email/confirm_email_copy.html"), name="preview123"),
    path('invite/', login_required()(InviteUserView.as_view()), name='invite'),
    path('outstanding_invites/', login_required()(OutstandingEventTeamInvites.as_view()), name='outstanding-invite'),
    path('request_role/<str:role>/', login_required()(RequestRole.as_view()), name='request-role'),


    re_path(r'^subscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<next>\w+)/', subscribe, name="subscribe_and_next"),
    re_path(r'^subscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', subscribe, name="subscribe"),
    re_path(r'^unsubscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<next>\w+)', unsubscribe,
            name="unsubscribe_and_next"),
    re_path(r'^unsubscribe/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', unsubscribe, name="unsubscribe"),




    path('get_image_data/', get_image_data, name="get_image_data"),  # this should be in a job


    path('explore/scores/<event_ref:event_ref>/', ExploreScores.as_view(), name="explore-scores"),
    path('explore/marks/<event_ref:event_ref>/', ExploreMarks.as_view(), name="explore-marks"),
    path('viz/', TemplateView.as_view(template_name="viz/line.html"), name="viz"),
    path('competition/results/<compref:compref>/', CompetitionResultsView.as_view(), name="competition-results"),  # viz bars

    # these select2 autocompletes used for multi-select only
    # path('organisers-autocomplete/', OrganisersAutocomplete.as_view(), name='organisers-autocomplete'),
    # path('scorers-autocomplete/', ScorersAutocomplete.as_view(), name='scorers-autocomplete'),
    # path('writers-autocomplete/', WritersAutocomplete.as_view(), name='writers-autocomplete'),
    # path('riders-autocomplete/', RidersAutocomplete.as_view(), name='riders-autocomplete'),
    # path('judges-autocomplete/', JudgesAutocomplete.as_view(), name='judges-autocomplete'),
    # #path('venue-autocomplete/', VenueAutocomplete.as_view(create_field='name'), name='venue-autocomplete'),
    # path('horse-autocomplete/', HorseAutocomplete.as_view(), name='horse-autocomplete'),
    # path('event-autocomplete/', EventAutocomplete.as_view(), name='event-autocomplete'),
    # path('testsheet-autocomplete/', TestSheetAutocomplete.as_view(), name='testsheet-autocomplete'),

    path('judgedashboard/', login_required()(JudgeAllEventsDashboard.as_view()),
         name="judge-all-events-dashboard"),

    path('', home, name="home"),

    path('score_obstacles/', login_required(ScoreObstacles.as_view()), name='score_fence'),


    path('enter/<event_ref:event_ref>/', login_required(EnterOnline.as_view()), name='enter-online'),
    #path('pay/<str:status>/', PayComplete.as_view(), name='payment'),
    #path('charge/', login_required(Charge.as_view()), name='charge'),
    path('fromstripe/', stripe_endpoint, name='stripe_endpoint'),    #TODO: block all but stripe
    path('order_paid/', stripe_endpoint, name='stripe_endpoint'),    #TODO: block all but stripe

    path('event/checklist/<event_ref:event_ref>/', EventsChecklist.as_view(), name="event-checklist"),
    path('event/checklist/', EventsChecklist.as_view(), name="event-checklist2"),
    path('event/printing/<event_ref:event_ref>/', EventPrinting.as_view(), name="event-printing"),

    path('event/dashboard/<int:user_id>/<str:ref>/', dashboard, name="dashboard-with-id"),
    path('event/dashboard/<event_ref:event_ref>/', dashboard, name="event-dashboard"),
    path('event/dashboard/<str:linktype>/<str:link>/', dashboard, name="event-dashboard-with-link"),
    path('event/dashboard/', dashboard, name="event-dashboard-no-ref"),

    # path('org-dashboard/<event_ref:event_ref>/', OrganiserDashboard.as_view(), name="organiser-dashboard"),
    # path('dash2/<event_ref:event_ref>/', OrganiserDashboard2.as_view(), name="organiser-dashboard"),
    # path('scorer-dashboard/<event_ref:event_ref>/', ScorerDashboard.as_view(), name="scorer-dashboard"),
    # path('writer-dashboard/<event_ref:event_ref>/', WriterDashboard.as_view(), name="writer-dashboard"),
    # path('org-dashboard/', OrganiserDashboard.as_view(), name="organiser-dashboard"),
    # path('scorer-dashboard/', ScorerDashboard.as_view(), name="scorer-dashboard"),
    # path('writer-dashboard/', WriterDashboard.as_view(), name="writer-dashboard"),

    # path('dashboard/<str:eventid>/', dashboard, name="dashboard"),
    # path('dashboard/', user_passes_test(has_role_manager)(OrganiserDashboard.as_view()), name="organiser-dashboard"),
    path('event/writer-dashboard/<event_ref:event_ref>/', login_required()(WriterDashboard.as_view()), name="writer-dashboard"),
    path('event/scorerdashboard/<event_ref:event_ref>/', login_required()(ScorerDashboard.as_view()), name="scorer-dashboard"),
    path('event/judgedashboard/<event_ref:event_ref>/<roleref:role_ref>/', login_required()(JudgeDashboard.as_view()), name="judge-dashboard"),
    path('event/judgedashboard/<event_ref:event_ref>/', login_required()(JudgeDashboard.as_view()), name="judge-dashboard"),

    path('event/orgdashbord/<event_ref:event_ref>/',login_required()(OrganiserDashboard.as_view()), name="organiser-dashboard"),
    path('rider-dashboard/<event_ref:event_ref>/', login_required()(RiderDashboard.as_view()), name="rider-dashboard"),
    path('rider-dashboard/', login_required()(RiderDashboard.as_view()), name="rider-dashboard"),

    path('myevents/', login_required()(EventsOverview.as_view()), name='myevents'),
    path('event/list/', login_required()(EventsOverview.as_view()), name='event_list'),


    path('event/judge_n_score/<sheetref:sheet_ref>/', JudgenScore.as_view(), name="judge-n-score"),
    path('event/judge_n_score/<compref:comp_ref>/', JudgenScore.as_view(), name="judge-n-score"),
    # path('event/add/<event_ref:event_ref>/', login_required()(EventCreate.as_view()), name='event-add-ref'),
    path('event/add/', login_required()(EventCreate.as_view()), name='event-add'),
    path('event/setup/<event_ref:event_ref>/', login_required()(EventSetup.as_view()), name='event-setup'),
    path('event/naming/<event_ref:event_ref>/', login_required()(EventNaming.as_view()), name='event-naming'),

    path('event/settings/dressage/<event_ref:event_ref>/', login_required()(EventUpdateDressage.as_view()),
         name='event-update-dressage'),
    path('event/update/<event_ref:event_ref>/', login_required()(EventUpdate.as_view()), name='event-update'),
    # manage judge pool and judges per competition for this event
    path('event/judges/<event_ref:event_ref>/', login_required()(EventJudges.as_view()), name='event-judges'),
    path('event/leaders/<event_ref:event_ref>/', login_required()(EventLeaders.as_view()), name='event-leaders'),
    # manage team, excluding judges, for this event
     path('event/team/<event_ref:event_ref>/add/', login_required()(EventTeamManageAdd.as_view()), name='event-team-add'),
     path('event/team/<event_ref:event_ref>/', login_required()(EventTeamManage.as_view()), name='event-team'),
    # accept invitation to join event team
     path('e/<int:id>/', login_required(eventteam_accept), name='eventteam-accept-short'),  # scodehort version for qr/direct entry
     # path('event/team/accept/<int:id>/', login_required(eventteam_accept), name='eventteam-accept'),
     path('event/team/accept/<str:longid>/', login_required(eventteam_accept), name='eventteam-accept-longid'),
     path('event/team/reject/<str:longid>/', login_required(eventteam_reject), name='eventteam-reject-longid'),


    path('event/online_entries_settings/<event_ref:event_ref>/', login_required()(EventOnlineEntriesSettingsUpdate.as_view()), name='online_entries_settings'),

    path('event/delete/<event_ref:event_ref>/', user_passes_test(has_role_manager)(EventDelete.as_view()), name='event-delete'),
    #path('event/browser/<event_ref:event_ref>/', login_required()(EventBrowser.as_view()), name='event-browser'),
    path('event/entries/<event_ref:event_ref>/', login_required()(BrowseEntries.as_view()), name='entry-browser'),
    path('event/arena/update/<int:pk>/', login_required()(EventArenaUpdate.as_view()), name='update-schedulearena'),

    path('event/entries/<event_ref:event_ref>/export/', login_required()(EventEntriesExport.as_view()), name='event-entries-export'),
    path('event/results/<event_ref:event_ref>/export/', login_required()(EventResultsExport.as_view()), name='event-results-export'),
    path('event/scores/<event_ref:event_ref>/export/', user_passes_test(has_role_manager)(event_scores_export), name='event-scores-export'),
    path('event/results/<event_ref:event_ref>/', EventResults.as_view(), name='event-results'),

    path('event/starttimes/<event_ref:event_ref>/export/', user_passes_test(has_role_manager)(event_starttimes_export), name='event-starttimes-export'),
    path('event/starttimes/<event_ref:event_ref>/export/xls/', user_passes_test(has_role_manager)(event_starttimes_export_xls), name='event-starttimes-export-xls'),

    path('event/starttimes/<event_ref:event_ref>/', EventStartTimes.as_view(), name='event-starttimes'),
    path('event/report/<event_ref:event_ref>/', CreateEventReport.as_view(), name='create_event_report'),
    path('event/scorer_record_sheet/<event_ref:event_ref>/', ScorerRecordSheet.as_view(), name='scorer-record-sheet'),
    path('event/result_record_sheet/<event_ref:event_ref>/', ResultRecordSheet.as_view(), name='result-record-sheet'),
    path('event/result_record_sheet/<compref:compref>/', ResultRecordSheet.as_view(), name='result-record-sheet-comp'),
    path('event/withdraw/<event_ref:event_ref>/', user_passes_test(has_role_manager)(WithdrawRiderHorse.as_view()), name='withdraw-riderhorse'),

    path('event/unassigned_images/<event_ref:event_ref>/', user_passes_test(has_role_manager)(UnassignedImageView.as_view()),
         name='event-unassigned'),

    path('event/close/<event_ref:event_ref>/', login_required()(EventClose.as_view()), name='event-close'),
    path('event/publish/<event_ref:event_ref>/', login_required()(EventPublish.as_view()), name='event-publish'),


    path('event/competitions/<event_ref:event_ref>/', login_required()(EventUpdateCompetitions.as_view()),
         name='update-competitions'),

    path('event/competition/create/<event_ref:event_ref>/', login_required()(CompetitionCreate.as_view()),
         name='competition-create'),

    #not currently used - same as event dashboard but just one competition
    path('event/competition/dashboard/<compref:compref>/', login_required()(CompetitionView.as_view()),
         name='competition-dashboard'),

    path('event/competition/<compref:compref>/', login_required()(CompetitionUpdate.as_view()),
         name='competition-update'),
    path('event/competition/<int:pk>/', login_required()(CompetitionUpdate.as_view()),
         name='competition-update'),

    path('event/competition/entries/<compref:compref>/', login_required()(CompetitionEntries.as_view()),
         name='competition-entries'),
    path('event/competition/<compref:compref>/delete/', login_required()(CompetitionDelete.as_view()),
         name='competition-delete'),

    path('upload/<entryref:entryref>/', login_required()(UploadEntrySubmission.as_view()), name='submission-upload'),
    path('entry/<entryref:entryref>/', login_required()(EntryCRUD.as_view()), name='entry-update'),
    path('entry/<int:entry_id>/', login_required()(EntryCRUD.as_view()), name='entry-update'),
    path('entry/<str:mode>/<int:entry_id>/', login_required()(EntryCRUD.as_view()), name='entry-update-with-mode'),
    path('event/add_entry/<event_ref:event_ref>/<compref:compref>/', login_required()(EntryCRUD.as_view()),
         name='add_entry_to_comp'),
    path('event/add_entry/<event_ref:event_ref>/', login_required()(EntryCRUD.as_view()),
         name='add_entry_to_event'),

    path('export_event/<int:eventid>/', export_event, name="export_event"),

    path('schedule/event/<event_ref:event_ref>/', Timeslots.as_view(), name="schedule-event"),
    path('schedule/<str:scheduleid>/', Timeslots.as_view(), name="schedule"),  # not currently used ?
    path('reschedule/event/<event_ref:event_ref>/', Reschedule.as_view(), name="reschedule-event"),
    path('unschedule/event/<event_ref:event_ref>/', Unschedule.as_view(), name="unschedule-event"),

    #path('upload_times/<int:event_id>/', user_passes_test(has_role_manager)(upload_entries), name='upload_times'),  # deprecated - use import_entries
    # path('upload_entries/<int:event_id>/', login_required()(UploadEntries.as_vew()), name='import_entries'), # deprecated - use import_entries
    # path('upload_results/<int:event_id>/', login_required()(UploadEntries.as_vew()), name='upload_results'),
    path('refresh_scoresheets/<int:compid>/', user_passes_test(has_role_manager)(refresh_scoresheets), name='refresh_scoresheets'),
    path('import_entries/<event_ref:event_ref>/', user_passes_test(has_role_manager)(UploadEntriesView.as_view()), name='upload_entries'),
    path('import_competitions/<event_ref:event_ref>/', user_passes_test(has_role_manager)(UploadCompetitionsView.as_view()), name='upload_competitions'),





    path('test/admin/clone/<int:id>/', user_passes_test(has_role_manager)(clone_testsheet), name='test-clone'),
    path('test/admin/clone_xml/<int:id>/', user_passes_test(has_role_manager)(update_testsheet_from_xml), name='test-clone-xml'),
    path('test/admin/list/<str:issuer>/', user_passes_test(has_role_manager)(TestListByIssuer.as_view()), name='test-list'),
    path('test/admin/<testref:ref>/', user_passes_test(has_role_manager)(TestUpdate.as_view()), name='test-update'),
    path('test/admin/<int:id>/', user_passes_test(has_role_manager)(TestUpdate.as_view()), name='test-update-id'),
    path('test/admin/', login_required()(TestList.as_view()), name='test-admin'),
    path('test/check/', login_required()(TestCheck.as_view()), name='test-check'),
    path('test/add/', user_passes_test(has_role_manager)(TestCreate.as_view()), name='test-add'),
    path('test/listen/<str:ref>/', Listen2Test.as_view(), name='test-listen'),
    path('test/download/<str:ref>/', download_test, name='test-download'),

    path('tests/', tests, name="tests"),







    path('tests/<str:eventid>/', tests, name="tests"),
    #path('tests_json/', user_passes_test(has_role_manager)(test_list), name='test_list'),
    path('test_pdf/testsheet/<int:testsheet>/', login_required()(EntriesPDF.as_view()), name='testsheet_pdf_example'),

    path('entry_pdf/entry/<entryref:entryref>/', login_required()(EntriesPDF.as_view()), name='entry_pdf'),
    path('entry_pdf/entry/<str:entryid>/', login_required()(EntriesPDF.as_view()), name='entry_pdf'),
    path('entry_pdf/comp/<compref:compref>/', login_required()(EntriesPDF.as_view()), name='comp_pdf'),
    path('entry_labels/comp/<compref:compref>/', login_required()(EntriesPDF.as_view()),{'format':'label'}, name='comp_labels'),
    path('entry_pdf/event/<event_ref:event_ref>/', login_required()(EntriesPDF.as_view()), name='event_pdf'),
    path('entry_labels/event/<event_ref:event_ref>/', login_required()(EntriesPDF.as_view()), {'format':'label'}, name='event_labels'),


    path('test_image_upload/', TemplateView.as_view(template_name='test_sheetimage_upload.html'), name='test_image_upload'),


    #path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('paytest/<event_ref:event_ref>/', paytest, name='pay'),



    path('issuer_testsheets/<int:issuer_id>/', user_passes_test(lambda u: u.is_superuser)(issuer_testsheets_xls), name="issuer_testsheets"),
    path('issuer_testsheets/', login_required()(issuer_testsheets_xls), name="issuer_testsheets"),

    path('event/<event_ref:event_ref>/', login_required()(EventHome.as_view()), name='event-home'),
    path('<event_ref:event_ref>/', login_required()(EventHome.as_view()), name='event-home'),
]

superuser_urlpatterns = [

    path('create_demo_from_event/<event_ref:event_ref>/', create_demo_from_event, name="create-demo"),

    path('check_event_data/<event_ref:event_ref>/fix/', check_event_data, {'fix': True}, name="check_event_data"),
    path('check_event_data/<event_ref:event_ref>/', check_event_data, name="check_event_data"),
    # path('exforimport/<int:eventid>/', export_eventx,),
    path('csvtestdata/', csvtestdata, name="csvtestdata"),
    path('mytestdata/', mytestdata, name="mytestdata"),
    path('create_missing_event_directories', create_missing_event_directories, name="create-missing-event-directories"),

    path('scrape_di_results/', scrape_di_results, name="scrape_di_results"),
    path('scrape_ei_results/', scrape_ei_results, name="scrape_ei_results"),
    path('scrape_ei_events/', scrape_ei_events, name="scrape_ei_events"),
    path('process_rider_results/', process_rider_results, name="process_rider_results"),
    path('make_resources/', make_resources, name="make_resources"),
    # path('fix_entryid/', fix_entryid, name="fix_entryid"),
    path('add_ref2entry/', add_ref2entry, name="add_ref2entry"),
    #path('update_searchable/', update_searchable, name="update_searchable"),
    # path('fix_sortable/', fix_sortable, name="fix_sortable"),
    # path('fix_judges/', fix_judges, name="fix_judges"),
    path('sync_testsheets/', sync_testsheets, name="sync_testsheets"),

    # resave all entries for an event - useful when bug fixing
    path('touch_entries/<event_ref:event_ref>/', touch_entries, name="touch_entries"),
    #path('fix_event_data/', fix_event_data, name="fix_event_data"),
    path('manage_roles/', user_passes_test(has_role_administrator)(ManageRoles.as_view()), name="manage_roles"),


# direct to ref patterns

    path('sheet/<sheetref:ref>/', SheetHomePage.as_view(), name="sheet-home2"), #deprecated
    path('<sheetref:ref>', SheetHomePage.as_view(), name='sheet_shortcut'),  # not lack of closing / - deprecated
    path('<sheetref:ref>/', SheetHomePage.as_view(), name='sheet-home'),
]

nologin_urlpatterns += [
    path('t/<testref:ref>/', user_passes_test(is_anon)(TestHomePage.as_view()), name='test-home'),

    path('<event_ref:event_ref>/', user_passes_test(is_anon)(EventPublic.as_view()), name='event-public'),
    path('<event_ref:event_ref>/scoreboard/', EventScoreboard.as_view(), name='event-scoreboard'),

    path('video_judge_demo/', TemplateView.as_view(template_name='video/demo.html'), name="video_judge_demo"),
    path('poster/<compref:compref>/', comp_poster, name="comp_poster"),
]

whinie = [
    path('', include('config.urls_whinie_api')),
    ]

# used during development
#path('auto/', TemplateView.as_view(template_name='test_autocomplete.html')),

urlpatterns = api_urlpatterns + library_urlpatterns + nologin_urlpatterns + login_required_urlpatterns + event_urlpatterns_login \
              + event_urlpatterns_organiser + superuser_urlpatterns + whinie

urlpatterns += static('.well-known/acme-challenge', document_root=challenge_dir)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.ASSETS_URL, document_root=settings.ASSETS_ROOT)
    urlpatterns += static(settings.EVENT_URL, document_root=settings.EVENT_ROOT)
    # urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    # import debug_toolbar
    #
    # urlpatterns = [
    #                   path('__debug__/', include(debug_toolbar.urls)),
    #               ] + urlpatterns
    #
