<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
    <title>Login</title>
    <link rel="stylesheet" type="text/css" href="${tg.url('/static/css/login.css')}" />
</head>

<body>
<div id="main_content">
    <div id="loginBox">
        <h1>Login</h1>
        <p>${message}</p>
        <form action="${previous_url}" method="POST">
            <table>
                <tr>
                    <td class="label">
                        <label for="user_name">User Name:</label>
                    </td>
                    <td class="field">
                        <input type="text" id="user_name" name="user_name"/>
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label for="password">Password:</label>
                    </td>
                    <td class="field">
                        <input type="password" id="password" name="password"/>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" class="buttons">
                        <input type="submit" name="login" value="Login"/>
                    </td>
                </tr>
            </table>

            <input py:if="forward_url" type="hidden" name="forward_url"
                value="${forward_url}"/>
                
            <input py:for="name,value in original_parameters.items()"
                type="hidden" name="${name}" value="${value}"/>
        </form>
    </div>
</div>
</body>
</html>
