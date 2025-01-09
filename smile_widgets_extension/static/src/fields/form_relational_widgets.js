/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {Many2ManyTagsFieldColorEditable} from "@web/views/fields/many2many_tags/many2many_tags_field";

const core = require('web.core');
const _t = core._t;

patch(Many2ManyTagsFieldColorEditable.prototype, "smile_tags", {
    onBadgeClick(ev, record) {
        return this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: `${_t("Open: ")} ${this.string}`,
            res_model: record.resModel,
            res_id: record.data.id,
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: {"create": false, "edit": false, "delete": false},
        });
    },

    template: 'web.Many2ManyTagsFieldColorEditable'
});
