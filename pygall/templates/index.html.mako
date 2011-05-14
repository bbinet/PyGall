<!DOCTYPE HTML>
<html lang="${lang}">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="Content-Language" content="${lang}" />

        <title>PyGall Pyramid application</title>

        <link rel="shortcut icon" type="image/x-icon" href="${request.static_url('pygall:static/app/img/favicon.ico')}" />

##% if debug:
##        <link rel="stylesheet" type="text/css" href="${request.static_url('pygall:static/app/css/main.css')}" />
##% else:
##        <link rel="stylesheet" type="text/css" href="${request.static_url('pygall:static/build/app.css')}" />
##% endif
##
##% if debug:
##        <script type="text/javascript" src="${request.static_url('pygall:static/app/lib/App/Lang/en.js')}"></script>
##        <script type="text/javascript" src="${request.static_url('pygall:static/app/lib/App/Lang/fr.js')}"></script>
##        <script type="text/javascript" src="${request.static_url('pygall:static/app/lib/App/main.js')}"></script>
##% else:
##        <script type="text/javascript" src="${request.static_url('pygall:static/build/app.js')}"></script>
##      ## we don't build a language file for english
##%     if lang != 'en':
##        <script type="text/javascript" src="${request.static_url('pygall:static/build/lang-%s.js' % lang)}"></script>
##%     endif
##% endif
        <script type="text/javascript">
            <%include file="globals.js.mako" />
        </script>
    </head>

    <body>
        <h1>Pygall home page</h1>
        <p>model.name = ${model.name}</p>
    </body>
</html>
