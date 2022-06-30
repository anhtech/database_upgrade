odoo.define('disable_odoo_online.ExpirationPanel', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var session = require('web.session');
var utils = require('web.utils');
var HomeMenu = require('web_enterprise.HomeMenu');

var QWeb = core.qweb;

HomeMenu.include({
    /**
     * Checks for the database expiration date and display a warning accordingly.
     *
     * @private
     */
    _enterpriseExpirationCheck: function () {
        var self = this;

        // don't show the expiration warning for portal users
        if (!(session.warning))  {
            return;
        }
        var today = new moment();
        // if no date found, assume 1 month and hope for the best
        var dbexpirationDate = new moment(new moment().add(30, 'd'));
        var duration = moment.duration(dbexpirationDate.diff(today));
        var options = {
            'diffDays': Math.round(duration.asDays()),
            'dbexpiration_reason': session.expiration_reason,
            'warning': session.warning,
        };
        self._enterpriseShowPanel(options);
    },
});

});

