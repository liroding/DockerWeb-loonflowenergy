from django.urls import path

from apps.workflow.views import StateView, WorkflowView, WorkflowInitView, WorkflowStateView, WorkflowRunScriptView, \
    WorkflowRunScriptDetailView, WorkflowCustomNoticeView, WorkflowCustomNoticeDetailView, WorkflowDetailView, \
    WorkflowTransitionView, WorkflowCustomFieldView, WorkflowCustomFieldDetailView, WorkflowStateDetailView, \
    WorkflowTransitionDetailView, WorkflowUserAdminView,WorkflowAllTicketData

urlpatterns = [
    path('', WorkflowView.as_view()),
    path('/user_admin', WorkflowUserAdminView.as_view()),
    path('/<int:workflow_id>/init_state', WorkflowInitView.as_view()),
    path('/<int:workflow_id>', WorkflowDetailView.as_view()),
    path('/<int:workflow_id>/states', WorkflowStateView.as_view()),
    path('/<int:workflow_id>/states/<int:state_id>', WorkflowStateDetailView.as_view()),
    path('/<int:workflow_id>/transitions', WorkflowTransitionView.as_view()),
    path('/<int:workflow_id>/transitions/<int:transition_id>', WorkflowTransitionDetailView.as_view()),
    path('/<int:workflow_id>/custom_fields', WorkflowCustomFieldView.as_view()),
    path('/<int:workflow_id>/custom_fields/<int:custom_field_id>', WorkflowCustomFieldDetailView.as_view()),

    path('/states/<int:state_id>', StateView.as_view()),
    path('/run_scripts', WorkflowRunScriptView.as_view()),
    path('/run_scripts/<int:run_script_id>', WorkflowRunScriptDetailView.as_view()),
    path('/custom_notices', WorkflowCustomNoticeView.as_view()),
    path('/custom_notices/<int:notice_id>', WorkflowCustomNoticeDetailView.as_view()),
    #add by liro   查找workflow_id对应的所有ticket_id,然后获取数据
    path('/<int:workflow_id>/download', WorkflowAllTicketData.as_view()),
    #add by liro   查找与username 相关的workflow
    path('/user', WorkflowView.as_view()),
]
