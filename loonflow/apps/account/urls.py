from django.urls import path
from apps.account.views import LoonUserView, LoonUserDetailView, LoonRoleView, LoonDeptView, LoonAppTokenView, LoonAppTokenDetailView, \
    LoonLoginView, LoonLogoutView, LoonUserRoleView, LoonRoleUserView, LoonUserResetPasswordView, LoonRoleDetailView, LoonDeptDetailView, \
    LoonRoleUserDetailView,\
LiroUserView ,LiroRoleUserView #, LoonRoleDetailView,LoonRoleUserDetailView

urlpatterns = [
    path('/users', LoonUserView.as_view()),
    path('/_users',LiroUserView.as_view()),  #add by liro
    path('/users/<int:user_id>', LoonUserDetailView.as_view()),
    path('/users/<int:user_id>/roles', LoonUserRoleView.as_view()),
    path('/users/<int:user_id>/reset_password', LoonUserResetPasswordView.as_view()),
    path('/roles', LoonRoleView.as_view()),
    path('/roles/<int:role_id>', LoonRoleDetailView.as_view()),
    path('/roles/<int:role_id>/users', LoonRoleUserView.as_view()),
    path('/roles/<int:role_id>/_users', LiroRoleUserView.as_view()),  #add by liro
    path('/roles/<int:role_id>/users/<int:user_id>', LoonRoleUserDetailView.as_view()),
    path('/depts', LoonDeptView.as_view()),
    path('/depts/<int:dept_id>', LoonDeptDetailView.as_view()),
    path('/login', LoonLoginView.as_view()),
    path('/logout', LoonLogoutView.as_view()),
    path('/app_token', LoonAppTokenView.as_view()),
    path('/app_token/<int:app_token_id>', LoonAppTokenDetailView.as_view()),
]
