<script>
    import { getViews, openViews } from './../services/menu.js';
    import { call } from './../services/service.js';
    import { updateGlobals, publish } from './../services/writables.js';
    import { requestReport } from './../services/report.js';
    import { getContext } from 'svelte';

    export let text;
    export let options;
    export let action;
    export let model;
    export let record;

    let { save } = getContext("formViewFunctions");

    function onClick() {
        if(record.id){
            doAction(record.id);
        }else{
            save().then((resp) => {
                doAction(resp);
                history.back();
            })
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
            getViews(options.model, options.view_types).then((resp) => openViews(resp));
        }else if(action == "method"){
            call(`${model}:${recordId}`, options.name).then(
                (resp) => {
                    publish({
                        'event': 'activeRecordIdChanged',
                        'id': recordId
                     })
                }
            );
        }else if(action == "report"){
            requestReport(options.report_name, [recordId])
        }
    }
</script>

<button type="button" class="btn {options.class || 'btn-secondary'}" on:click={onClick}>
    {text}
</button>
