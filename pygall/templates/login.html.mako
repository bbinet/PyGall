# -*- coding: utf-8 -*-
<%inherit file="base.html.mako"/>\
<h3>${_('Login')}</h3><br/>
<span>${message}</span>
<form action="${request.route_path('login')}" method="post">
    <input type="hidden" name="came_from" value="${came_from}"/>
    <input type="text" name="login" value="${login}"/><br/>
    <input type="password" name="password" /><br/>
    <input type="submit" name="form.submitted" value="Log In"/>
</form>
