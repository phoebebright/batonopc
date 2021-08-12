from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import ugettext_lazy as _

from .models import *
from .serializers import *
from .metrics import active_gadgets_detail
from .filters import GadgetLogGlobalFilter

#TODO: move to toolbox/gadget_base

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class GadgetViewSet(viewsets.ModelViewSet):

    queryset = Gadget.objects.all()
    serializer_class = GadgetShortSerializer
    lookup_field = 'factory_id'
    pagination_class = None



    def get_queryset(self):

        if self.request.user.is_gadget_admin() or self.request.user.is_workflow_user():
            qs = Gadget.objects.all()
        else:
            qs = Gadget.objects.mine(self.request.user)

        return qs.prefetch_related('gadget_model', 'owner', 'creator')

    # # for debugging qs speed
    # @query_debugger
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)


    def has_object_permission(self, request, view, obj):

        me = request.user
        org = obj.organisation

        # only users from an organisation can view edt data
        if request.method in permissions.SAFE_METHODS and org and me.organisation == org:
            return True

        elif me.can_change_edt():
            return True

        return False

    @action(detail=True, methods=['post'])
    def add2log(self, request, pk=None, factory_id=None):
        gadget = self.get_object()

        try:
            # why is this required?
            data = request.data.dict()
        except:
            data = request.data


        data['gadget'] = gadget.id
        data['creator'] = request.user.id

        # when - default to now
        if not 'when' in request.data:
            data['when'] = timezone.now()

        # who
        if 'who' in request.data:
            if request.data['who'] == request.user.email:
                data['who'] = data['creator']
            else:
                try:
                    data['who'] = OrgUser.objects.get(email=request.data['who'])
                except OrgUser.DoesNotExist:
                    data['who'] = OrgUser.objects.get(id=request.data['who'])

        else:
            data['who'] = data['creator']

        serializer = GadgetLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['patch'])
    def update_baseline(self, request, pk=None, factory_id=None):
        gadget = self.get_object()

        kwargs = {}
        if 'we_baseline' in request.data:
            kwargs['we0'] = int(request.data['we_baseline'])
        if 'ae_baseline' in request.data:
            kwargs['ae0'] = int(request.data['ae_baseline'])
        if 'sensitivity' in request.data:
            kwargs['sensitivity'] = int(request.data['sensitivity'])

        if kwargs:
            gadget.update_edt_calibrations(request.user, **kwargs)

        return Response("OK")



class GadgetLogViewset(viewsets.ModelViewSet):
    '''return list of log entries filtered according to gadget reference '''
    queryset = GadgetLog.objects.none()
    serializer_class = GadgetLogSerializer
    http_method_names = ['get','post']

    pagination_class = StandardResultsSetPagination
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['factory_id', 'action_type', 'action']
    # ordering_fields = ['factory_id', 'action_type', 'action', 'when', 'creator']
    # ordering = ['-when']

    def get_queryset(self):

        # check that user has access to this gadget and only return entries for one gadget
        org = self.request.user.organisation_id
        queryset = GadgetLog.objects.filter(owner_key=org).order_by('-when')
        ref = self.request.query_params.get('ref', None)
        if ref is not None:
            queryset = queryset.filter(gadget_ref=ref)

        return queryset.prefetch_related('gadget',  'creator')

    def perform_create(self, serializer):
        serializer.save()


class GadgetLogListViewset(generics.ListAPIView):
    #TODO: this can probably be replaced by Uploads Viewset
    serializer_class = GadgetLogSerializer

    queryset = GadgetLog.objects.all().order_by('-when')
    http_method_names = ['get', ]
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = GadgetLogGlobalFilter

    def get_queryset(self):
        '''queryset depends on user'''

        me = self.request.user

        gadget = Gadget.objects.get(ref=self.kwargs['gadget_ref'])

        # check this user can view this gadget
        if not gadget.can_view(me):
            return GadgetLog.objects.none()

        qs = GadgetLog.objects.filter(gadget_ref=self.kwargs['gadget_ref']).order_by('-when')


        return qs


class ActiveGadgets(APIView):
    '''list of recently seen gadgets for this user'''
    http_method_names = ['get',]

    def get(self, request, *args, **kwargs):

        active_gadgets = active_gadgets_detail(request.user, "EDT2")
        gadget_list = [g for (g, _, _) in active_gadgets]



        qs = Gadget.objects.filter(factory_id__in=gadget_list)
        serializer = GadgetSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyEDTs(APIView):
    '''list of recently seen gadgets for this user'''
    http_method_names = ['get','post']
    authentication_classes = [
        'django_keycloak.auth.backends.ThirdPartyToken',]

    def get(self, request, *args, **kwargs):

        qs = Gadget.objects.mine(request.user)
        serializer = GadgetFactoryIDSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

#
# @csrf_exempt
# def my_edts(request):
#     logger = getLogger('django')
#
#     edts = []
#     subject_user = None
#
#     # current user
#     if request.user.is_authenticated:
#         logger.debug("User is authenticated, no Oauth checks")
#         subject_user = request.user
#     elif not request.headers.get('Authorization', '').startswith('Bearer '):
#         logger.debug("No Oauth authorization header")
#     elif not OauthRealm:
#         logger.warning("Dkango_keycloak not loaded")
#     else:
#         userinfo_endpoint = None
#         realm = OauthRealm.objects.first()
#         if realm:
#             well_known = realm.well_known_oidc
#             userinfo_endpoint = well_known['userinfo_endpoint']
#             valid_issuer = well_known['issuer']
#         else:
#             logger.warning("No Oauth realms configured")
#
#         authorization = request.headers.get('Authorization')
#         provided_origin = request.headers.get('Origin')
#
#         try:
#             encoded_token = authorization[len('Bearer '):].split('.')[1]
#             token = json.loads(b64decode(encoded_token + "==="))
#         except Exception as e:
#             logger.warning(f"Error parsing token: {e}")
#             token = {}
#
#         provided_issuer = token.get('iss')
#         allowed_origins = token.get('allowed-origins')
#
#         # do some prevalidation -- at least to be sure that nobody tries to hang up keycloak with trash
#         if not userinfo_endpoint:
#             logger.warning("No userinfo endpoint configured, skipping OAuth flow")
#         elif not (valid_issuer and provided_issuer == valid_issuer):
#             logger.warning(f"Ignoring Oauth token, wrong issuer (valid={valid_issuer}, provided={provided_issuer}")
#         elif not (allowed_origins and provided_origin and (provided_origin in allowed_origins)):
#             logger.warning(
#                 f"Ignoring Oauth token, origins mismatch (provided: {provided_origin}, allowed: {allowed_origins}")
#         else:
#             # now we're doing requet to keycloak to really validate the token
#             # as the token was issued for the requesting API and we do not have secret key to validate it (but keycloak does)
#             try:
#                 userinfo = requests.get(userinfo_endpoint, headers={"Authorization": authorization})
#                 usermail = userinfo.json()['email']
#                 subject_user = User.objects.filter(email=usermail).first()
#             except Exception as e:
#                 logger.warning(f"Failed to fetch user info, error: {e}")
#                 subject_user = None
#
#     if not subject_user:
#         logger.warning("Subject user not defined, returning empty list")
#     else:
#         logger.debug(f"Gathering EDTs for user {subject_user.email}")
#         edts = Gadget.objects.mine(subject_user).values_list('factory_id', flat=True)
#
#     # we need to return 200 response even if user is not authorized, to avoid grafana errors
#     return JsonResponse([e for e in edts], safe=False)
