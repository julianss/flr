<script>
    import { getViews, openViews, clickMenu } from './../services/menu.js';
    import { call } from './../services/service.js';
    import { updateGlobals, publish } from './../services/writables.js';
    import { requestReport } from './../services/report.js';
    import { updateHash, parseHash, replaceHash } from './../services/utils.js';
    import { getContext } from 'svelte';

    export let text;
    export let options;
    export let action;
    export let model;
    export let record;
    let disabled = false;

    let { save } = getContext("formViewFunctions");

    function onClick(event) {
        if (event && !(event.detail === 1)){
            return
        }
        if(record.id){
            doAction(record.id);
        }else{
            save().then((resp) => {
                doAction(resp);
            })
        }
    }

    function wrapFunctionOnClick(event){
        disabled = true;
        try {
            onClick(event)
        }
        finally {
            disabled = false;
        }
    }

    function doAction(recordId){
        if(options && options.globals){
            for(let k in options.globals){
                let code = "return " + options.globals[k];
                let value = new Function(code).call(record);
                updateGlobals(k, value);
            }
        }
        if(action == "openViews"){
            //If menu_id is present it behaves as if the menu was clicked
            //otherwise, it behaves as a wizard
            if(options.menu_id){
                clickMenu(options.menu_id);
            }else{
                getViews(options.model, ["form"]).then(
                    (resp) => {
                        openViews(resp, {
                            asWizard: true,
                            showSaveButton: options.saveButton
                        })
                        updateHash({'w': 1})
                    }
                )
            }
        }else if(action == "method"){
            call(`${model}:${recordId}`, options.name).then(
                (resp) => {
                    if(options.close){
                        history.back();
                    }else{
                        publish({
                            event: 'activeRecordIdChanged',
                            id: recordId
                        })
                    }
                }
            );
        }else if(action == "report"){
            requestReport(options.report_name, [recordId], function() {
                if(options.close){
                    history.back();
                }
            })
        }
    }
</script>

<button type="button" class="btn {options.class || 'btn-secondary'}" on:click={wrapFunctionOnClick} disabled="{disabled}">
    {text}
</button>
