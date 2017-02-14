from flask_assets import Bundle

def create_assets(assets):

    js = Bundle(
        'js/jquery.min.js',
        'js/tether.js',
        'js/bootstrap.min.js',
        'js/googlebutton.js',
        filters='rjsmin',
        output='js/libs.js'
    )
    assets.register('js_bootstrap', js)


    css = Bundle(
        'css/reset.css',
        'css/bootstrap.css',
        filters='cssmin',
        output='css/min.css'
    )

    assets.register('css_bootstrap', css)

    angular = Bundle(
        'angular/angular.js',
        'angular/app.js',
        filters='rjsmin',
        output='js/libs.js'
    )
    assets.register('js_angular', angular)
