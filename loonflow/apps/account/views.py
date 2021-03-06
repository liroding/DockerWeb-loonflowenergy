import json

from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from service.account.account_base_service import account_base_service_ins
from service.format_response import api_response
from apps.loon_base_view import LoonBaseView
from schema import Schema, Regex, And, Or, Use, Optional

from service.permission.manage_permission import manage_permission_check

####################################################################
#背景：workflow 用户端需要获取用户列表以及角色用户
#问题：loonflow 原本提供了相关函数，但是需要登录验证才可以使用
#解决：保持loonflow 函数，不做修改，重写新函数。
class LiroUserView(LoonBaseView):
    def get(self, request, *args, **kwargs):
        """
        获取用户列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        
        request_data = request.GET
        search_value = request_data.get('search_value', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        flag, result = account_base_service_ins.get_user_list(search_value, page, per_page)
        if flag is not False:
            data = dict(value=result.get('user_result_object_format_list'),
                        per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'),
                        total=result.get('paginator_info').get('total'))
            code, msg,  = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)


class LiroRoleUserView(LoonBaseView):

    def get(self, request, *args, **kwargs):
        print('[liro-debug] enter user view LiroRoleUserView')
        """
        角色的用户信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id', 0)
        search_value = request.GET.get('search_value', '')
        flag, result = account_base_service_ins.get_role_user_info_by_role_id(role_id, search_value)

        if flag is not False:
            data = dict(value=result.get('user_result_format_list'), per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'), total=result.get('paginator_info').get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    def post(self, request, *args, **kwargs):
        """
        add role's user
        新增角色用户
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id', 0)
        creator = request.user.username
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        user_id = request_data_dict.get('user_id', 0)

        flag, result = account_base_service_ins.add_role_user(role_id, user_id, creator)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})

########################################################################

@method_decorator(login_required, name='dispatch')
class LoonUserView(LoonBaseView):
    def __init__(self, *args, **kwargs):
        print('[liro-debug] enter user view 1')
    post_schema = Schema({
        'username': And(str, lambda n: n != '', error='username is needed'),
        'alias': And(str, lambda n: n != '', error='alias is needed'),
        'email': And(str, lambda n: n != '', error='alias is needed'),
        Optional('password'): str,
        'phone': str,
        'dept_id': And(int, lambda n: n > 0),
        'is_active': Use(bool),
        'is_admin': Use(bool),
        'is_workflow_admin': Use(bool),
    })

    @manage_permission_check('workflow_admin')
    def get(self, request, *args, **kwargs):
        """
        获取用户列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        print('[liro-debug] enter user view 2')
        request_data = request.GET
        search_value = request_data.get('search_value', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        flag, result = account_base_service_ins.get_user_list(search_value, page, per_page)
        if flag is not False:
            data = dict(value=result.get('user_result_object_format_list'),
                        per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'),
                        total=result.get('paginator_info').get('total'))
            code, msg,  = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        add user
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        if not json_str:
            return api_response(-1, 'post参数为空', {})
        request_data_dict = json.loads(json_str)
        username = request_data_dict.get('username')
        alias = request_data_dict.get('alias')
        email = request_data_dict.get('email')
        password = request_data_dict.get('password')
        phone = request_data_dict.get('phone')
        dept_id = int(request_data_dict.get('dept_id'))
        is_active = request_data_dict.get('is_active')
        is_admin = request_data_dict.get('is_admin')
        is_workflow_admin = request_data_dict.get('is_workflow_admin')
        creator = request.user.username
        flag, result = account_base_service_ins.add_user(username, alias, email, phone, dept_id, is_active, is_admin,
                                                     is_workflow_admin, creator, password)
        if flag is False:
            code, msg, data = -1, result, {}
        else:
            code, msg, data = 0, '', result
        return api_response(code, msg, data)


@method_decorator(login_required, name='dispatch')
class LoonUserDetailView(LoonBaseView):
    patch_schema = Schema({
        'username': And(str, lambda n: n != ''),
        'alias': And(str, lambda n: n != ''),
        'email': And(str, lambda n: n != ''),
        Optional('password'): str,
        'phone': str,
        'dept_id': And(int, lambda n: n > 0),
        'is_active': Use(bool),
        'is_admin': Use(bool),
        'is_workflow_admin': Use(bool),
    })

    @manage_permission_check('admin')
    def patch(self, request, *args, **kwargs):
        """
        edit user
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        user_id = kwargs.get('user_id')
        request_data_dict = json.loads(json_str)
        username = request_data_dict.get('username')
        alias = request_data_dict.get('alias')
        email = request_data_dict.get('email')
        phone = request_data_dict.get('phone')
        dept_id = request_data_dict.get('dept_id')
        is_active = request_data_dict.get('is_active')
        is_admin = request_data_dict.get('is_admin')
        is_workflow_admin = request_data_dict.get('is_workflow_admin')
        flag, result = account_base_service_ins.edit_user(user_id, username, alias, email, phone, dept_id, is_active,
                                                      is_admin, is_workflow_admin)
        if flag is not False:
            code, msg, data = 0, '', {}
        else:
            code, msg, data = -1, result, {}
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def delete(self, request, *args, **kwargs):
        """
        delete user record
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user_id = kwargs.get('user_id')
        flag, result = account_base_service_ins.delete_user(user_id)
        if flag:
            code, msg, data = 0, '', {}
            return api_response(code, msg, data)
        code, msg, data = -1, result, {}
        return api_response(code, msg, data)


@method_decorator(login_required, name='dispatch')
class LoonRoleView(LoonBaseView):
    post_schema = Schema({
        'name': And(str, lambda n: n != ''),
        Optional('description'): str,
        Optional('label'): str,
    })

    @manage_permission_check('admin')
    def get(self, request, *args, **kwargs):
        """
        用户角色列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        search_value = request_data.get('search_value', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        flag, result = account_base_service_ins.get_role_list(search_value, page, per_page)
        if flag is not False:
            data = dict(value=result.get('role_result_object_format_list'),
                        per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'),
                        total=result.get('paginator_info').get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        add role
        新增角色
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        name = request_data_dict.get('name')
        description = request_data_dict.get('description', '')
        label = request_data_dict.get('label', '')
        creator = request.user.username

        flag, result = account_base_service_ins.add_role(name=name, description=description, label=label,
                                                         creator=creator)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, result, {})


@method_decorator(login_required, name='dispatch')
class LoonRoleDetailView(LoonBaseView):
    patch_schema = Schema({
        'name': And(str, lambda n: n != '', error='name is need'),
        Optional('description'): str,
        Optional('label'): str,
    })

    @manage_permission_check('admin')
    def patch(self, request, *args, **kwargs):
        """
        update role
        更新角色信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id')
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        name = request_data_dict.get('name')
        description = request_data_dict.get('description')
        label = request_data_dict.get('label')
        flag, result = account_base_service_ins.update_role(role_id, name, description, label)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})

    @manage_permission_check('admin')
    def delete(self, request, *args, **kwargs):
        """
        delete role
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id')
        flag, result = account_base_service_ins.delete_role(role_id)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})


@method_decorator(login_required, name='dispatch')
class LoonDeptView(LoonBaseView):
    post_schema = Schema({
        'name': And(str, lambda n: n != ''),
        Optional('parent_dept_id'): int,
        Optional('leader'): str,
        Optional('approver'): str,
        Optional('label'): str,
    })

    @manage_permission_check('admin')
    def get(self, request, *args, **kwargs):
        """
        部门列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        search_value = request_data.get('search_value', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        flag, result = account_base_service_ins.get_dept_list(search_value, page, per_page)
        if flag is not False:
            paginator_info = result.get('paginator_info')
            data = dict(value=result.get('dept_result_object_format_list'), per_page=paginator_info.get('per_page'),
                        page=paginator_info.get('page'), total=paginator_info.get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        新增部门
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        name = request_data_dict.get('name')
        parent_dept_id = request_data_dict.get('parent_dept_id')
        leader_id = request_data_dict.get('leader')
        approver_str = request_data_dict.get('approver')
        approver_str_list = approver_str.split(',')
        label = request_data_dict.get('label')
        creator = request.user.username
        approver_id_list = [int(approver_str) for approver_str in approver_str_list]
        if approver_id_list:
            flag, result = account_base_service_ins.get_user_name_list_by_id_list(approver_id_list)
            if flag is False:
                return api_response(-1, result, {})
            approver_username_list = result.get('username_list')
            approver_username_str = ','.join(approver_username_list)
        else:
            approver_username_str = ''

        if leader_id:
            flag, result = account_base_service_ins.get_user_by_user_id(int(leader_id))
            if flag is False:
                return api_response(-1, result, {})
            leader = result.username
        else:
            leader = ''
        flag, result = account_base_service_ins.add_dept(name, parent_dept_id, leader, approver_username_str, label, creator)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, result, {})


@method_decorator(login_required, name='dispatch')
class LoonDeptDetailView(LoonBaseView):
    patch_schema = Schema({
        'name': And(str, lambda n: n != '', error='name is need'),
        Optional('parent_dept_id'): int,
        Optional('leader'): str,
        Optional('approver'): str,
        Optional('label'): str,
    })

    @manage_permission_check('admin')
    def delete(self, request, *args, **kwargs):
        """
        delete dept
        删除部门
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        operator = request.user.username
        dept_id = kwargs.get('dept_id')
        flag, result = account_base_service_ins.delete_dept(dept_id)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})

    @manage_permission_check('admin')
    def patch(self, request, *args, **kwargs):
        """
        更新部门
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        dept_id = kwargs.get('dept_id')
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        name = request_data_dict.get('name')
        parent_dept_id = request_data_dict.get('parent_dept_id')
        leader_id = request_data_dict.get('leader')
        approver = request_data_dict.get('approver')
        if approver:
            approver_list = approver.split(',')
            approver_id_list = [int(approver_str) for approver_str in approver_list]
        else:
            approver_id_list = []
        label = request_data_dict.get('label')

        if leader_id:
            ok, result = account_base_service_ins.get_user_by_user_id(
                int(leader_id)
            )
            if not ok:
                return api_response(-1, result, {})
            leader = result.username
        else:
            leader = None

        if approver_id_list:
            flag, result = account_base_service_ins.get_user_name_list_by_id_list(approver_id_list)
            if flag is False:
                return api_response(-1, result, {})
            approver_username_list = result.get('username_list')
            approver_username_str = ','.join(approver_username_list)
        else:
            approver_username_str = ''

        flag, result = account_base_service_ins.update_dept(dept_id,name, parent_dept_id, leader,
                                                             approver_username_str, label)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})


@method_decorator(login_required, name='dispatch')
class LoonAppTokenView(LoonBaseView):
    post_schema = Schema({
        'app_name': And(str, lambda n: n != '', error='app_name is needed'),
        Optional('ticket_sn_prefix'): str,
        'workflow_ids': And(str, lambda n: n != '', error='workflow_ids is needed'),
    })

    @manage_permission_check('admin')
    def get(self, request, *args, **kwargs):
        """
        call api permission
        调用权限列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        search_value = request_data.get('search_value', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        flag, result = account_base_service_ins.get_token_list(search_value, page, per_page)
        if flag is not False:
            paginator_info = result.get('paginator_info')
            data = dict(value=result.get('token_result_object_format_list'), per_page=paginator_info.get('per_page'),
                        page=paginator_info.get('page'), total=paginator_info.get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        add call api permission
        新增调用权限记录
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        app_name = request_data_dict.get('app_name', '')
        ticket_sn_prefix = request_data_dict.get('ticket_sn_prefix', '')
        workflow_ids = request_data_dict.get('workflow_ids', '')
        username = request.user.username
        flag, result = account_base_service_ins.add_token_record(app_name, ticket_sn_prefix, workflow_ids, username)
        if flag is False:
            code, data = -1, {}
        else:
            code, data = 0, {'id': result.get('app_token_id')}

        return api_response(code, result, data)


@method_decorator(login_required, name='dispatch')
class LoonAppTokenDetailView(LoonBaseView):
    patch_schema = Schema({
        'app_name': And(str, lambda n: n != '', error='app_name is needed'),
        Optional('ticket_sn_prefix'): str,
        'workflow_ids': And(str, lambda n: n != '', error='workflow_ids is needed'),
    })

    @manage_permission_check('admin')
    def patch(self, request, *args, **kwargs):
        """
        编辑token
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        app_token_id = kwargs.get('app_token_id')
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        app_name = request_data_dict.get('app_name', '')
        ticket_sn_prefix = request_data_dict.get('ticket_sn_prefix', '')
        workflow_ids = request_data_dict.get('workflow_ids', '')
        flag, msg = account_base_service_ins.update_token_record(app_token_id, app_name, ticket_sn_prefix, workflow_ids)
        if flag is False:
            code, data = -1, {}
        else:
            code, data = 0, {}

        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def delete(self, request, *args, **kwargs):
        """
        删除记录
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        app_token_id = kwargs.get('app_token_id')
        flag, msg = account_base_service_ins.del_token_record(app_token_id)
        if flag is False:
            code, data = -1, {}
        else:
            code, data = 0, {}
        return api_response(code, msg, data)


class LoonLoginView(LoonBaseView):
    def post(self, request, *args, **kwargs):
        """
        登录验证
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        json_str = request.body.decode('utf-8')
        if not json_str:
            return api_response(-1, 'patch参数为空', {})
        request_data_dict = json.loads(json_str)
        username = request_data_dict.get('username', '')
        password = request_data_dict.get('password', '')
        try:
            user = authenticate(username=username, password=password)
        except Exception as e:
            return api_response(-1, e.__str__(), {})

        if user is not None:
            login(request, user)
            return api_response(0, '', {})
        else:
            return api_response(-1, 'username or password is invalid', {})


class LoonLogoutView(LoonBaseView):
    def get(self, request, *args, **kwargs):
        """
        注销
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        logout(request)
        return redirect('/manage')


@method_decorator(login_required, name='dispatch')
class LoonUserRoleView(LoonBaseView):
    @manage_permission_check('admin')
    def get(self, request, *args, **kwargs):
        """
        用户角色信息
        """
        user_id = kwargs.get('user_id', 0)
        search_value = request.GET.get('search_value', '')
        flag, result = account_base_service_ins.get_user_role_info_by_user_id(user_id, search_value)
        if flag is not False:
            data = dict(value=result.get('role_result_format_list'), per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'), total=result.get('paginator_info').get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)


@method_decorator(login_required, name='dispatch')
class LoonRoleUserView(LoonBaseView):
    post_schema = Schema({
        'user_id': And(int, error='user_id is needed and should be int')
    })

    @manage_permission_check('admin')
    def get(self, request, *args, **kwargs):
        """
        角色的用户信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id', 0)
        search_value = request.GET.get('search_value', '')
        flag, result = account_base_service_ins.get_role_user_info_by_role_id(role_id, search_value)

        if flag is not False:
            data = dict(value=result.get('user_result_format_list'), per_page=result.get('paginator_info').get('per_page'),
                        page=result.get('paginator_info').get('page'), total=result.get('paginator_info').get('total'))
            code, msg, = 0, ''
        else:
            code, data = -1, ''
        return api_response(code, msg, data)

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        add role's user
        新增角色用户
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        role_id = kwargs.get('role_id', 0)
        creator = request.user.username
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        user_id = request_data_dict.get('user_id', 0)

        flag, result = account_base_service_ins.add_role_user(role_id, user_id, creator)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})


@method_decorator(login_required, name='dispatch')
class LoonRoleUserDetailView(LoonBaseView):
    @manage_permission_check('admin')
    def delete(self, request, *args, **kwargs):
        """
         delete role's user
         删除角色用户
         :param request:
         :param args:
         :param kwargs:
         :return:
         """
        user_id = kwargs.get('user_id', 0)
        role_id = kwargs.get('role_id', 0)
        flag, result = account_base_service_ins.delete_role_user(user_id,role_id)

        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, '', {})


class LoonUserResetPasswordView(LoonBaseView):

    @manage_permission_check('admin')
    def post(self, request, *args, **kwargs):
        """
        重置密码
        :param requesdt:
        :param args:
        :param kwargs:
        :return:
        """
        user_id = kwargs.get('user_id')
        flag, result = account_base_service_ins.reset_password(user_id=user_id)
        if flag is False:
            return api_response(-1, result, {})
        return api_response(0, result, {})
