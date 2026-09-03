import { patch } from '@web/core/utils/patch';
import { FormLabel } from '@web/views/form/form_label';
import { fieldVisualFeedback } from '@web/views/fields/field';

// Mark required fields with a trailing "*" on their form-view label.
// `fieldVisualFeedback().required` already accounts for both the Python
// `required=True` and any XML required expression evaluated on the record,
// and it is reactive, so the asterisk appears/disappears as the state changes.
patch(FormLabel.prototype, {
    get isRequiredField() {
        return fieldVisualFeedback(
            this.props.fieldInfo.field,
            this.props.record,
            this.props.fieldName,
            this.props.fieldInfo
        ).required;
    },
});
