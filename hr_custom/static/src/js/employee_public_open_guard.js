import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { FormController } from "@web/views/form/form_controller";

// Chặn mở form của nhân viên khác (không phải mình / cấp dưới) khi user không
// thuộc nhóm HR. Bấm vào không mở gì, vẫn ở màn list/kanban, không popup.
const MODEL = "hr.employee.public";

function isBlocked(controller, record) {
    return (
        controller.props.resModel === MODEL &&
        record &&
        record.data &&
        record.data.can_open_form === false
    );
}

patch(ListController.prototype, {
    async openRecord(record, options) {
        if (isBlocked(this, record)) {
            return;
        }
        return super.openRecord(record, options);
    },
});

patch(KanbanController.prototype, {
    async openRecord(record, options) {
        if (isBlocked(this, record)) {
            return;
        }
        return super.openRecord(record, options);
    },
});

// Chặn cả khi vào form bằng URL trực tiếp: nếu không được phép -> đưa về
// directory (kanban), không popup.
patch(FormController.prototype, {
    setup() {
        super.setup();
        if (this.props.resModel === MODEL) {
            this._ofbAction = useService("action");
            onMounted(() => {
                const root = this.model.root;
                if (root && root.data && root.data.can_open_form === false) {
                    this._ofbAction
                        .doAction("hr.hr_employee_public_action", { clearBreadcrumbs: true })
                        .catch(() => {});
                }
            });
        }
    },
});
