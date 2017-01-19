from flask_assets import Bundle

def create_assets(assets):

    js = Bundle(
        'js/material.js',
        'js/googlebutton.js',
        'js/jquery.min.js',
        filters='rjsmin',
        output='js/libs.js'
    )
    assets.register('js_material', js)


    css = Bundle(
        'css/material.css',
        'css/styles.css',
        filters='cssmin',
        output='css/min.css'
    )

    assets.register('css_material', css)

    angular = Bundle(
        'angular/angular.js',
        'angular/app.js',
        filters='rjsmin',
        output='js/libs.js'
    )
    assets.register('js_angular', angular)