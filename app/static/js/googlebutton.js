(function() {
    var i,
        oauthButtons = document.querySelectorAll('#js-google-oauth-login'),
        l = oauthButtons.length;

    var OauthLogin =  function (button) {
        this.init(button);
    };

    OauthLogin.prototype = {

        /**
         * @type {String}
         */
        oauthUrl: null,

        successTimeout: 20000,

        device: null,

        name: null,

        /**
         * @type {String}
         */
        redirectUrl: null,

        /**
         * @type {String}
         */
        popupWindowName: null,

        /**
         * @type {Array}
         */
        popupWindowParams: null,

        init: function (button) {
            var _this = this;

            this.oauthUrl = button.href;
            this.name = this._dataGet(button, 'name');
            this.device = this._dataGet(button, 'device');

            //get redirect url for success login
            this.redirectUrl = this._dataGet(button, 'redirect');

            this._addEvent(button, 'click', function (e) {
                e.preventDefault();
                _this.oauthLogin();
            });
        },

        oauthLogin: function () {
            var popupW, popupH, oauthPopup;

            popupW = 450;
            popupH = 600;


            if (this.device === 'mobile') {
                window.location.href = this.oauthUrl;
                return;
            }

            this.popupWindowName = 'oauth_' + this.name;
            var availLeft = (window.screen && window.screen.availLeft) ? window.screen.availLeft : 0;
            this.popupWindowParams = [
                'height=' + popupH,
                'width=' + popupW,
                'left=' + (availLeft + window.screen.width / 2 - popupW / 2),
                'top=' + (Math.max((window.screen.height / 2 - popupH/2 - 20), 0)),
                'scrollbars=1'
            ].join(',');

            oauthPopup = window.open(this.oauthUrl , this.popupWindowName, this.popupWindowParams);
            oauthPopup.focus();
        },

        _addEvent: function (el, type, handler) {
            if (el.addEventListener) {
                el.addEventListener(type, handler, false);
            } else {
                el.attachEvent('on' + type, handler);
            }
        },

        _dataGet: function (node, attr) {
            var
            // replace namesLikeThis with names-like-this
                toDashed = function (name) {
                    return name.replace(/([A-Z])/g, function(u) {
                        return "-" + u.toLowerCase();
                    })
                };

            if (document.head && document.head.dataset) {
                return node.dataset[attr];
            } else {
                return node.getAttribute('data-' + toDashed(attr));
            }
        }
    };

    for (i = 0; i <l; i++) {
        new OauthLogin(oauthButtons[i]);
    }

})();