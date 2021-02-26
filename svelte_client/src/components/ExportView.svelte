<script>
    import { call } from '../services/service.js';
    import { downloadReport } from '../services/report.js';
    export let model;
    export let selectedFields = [];
    export let filters = [];
    export let page;
    export let pageSize;
    export let selectedRecords;
    let exportOption = "current";
    let allFields = [];
    $: {
        if(model){
            call(model, "get_fields", {with_verbose_name:true}).then(
                (resp) => {
                    allFields = resp;
                }
            )
        }
    }

    function getSelectedIds(){
        var ids = [];
        for(let id in selectedRecords){
            if(selectedRecords[id]){
                ids.push(parseInt(id));
            }
        }
        return ids;
    }

    function doExport() {
        let args = [];
        let kwargs = {};
        args.push(selectedFields);
        if(filters.size > 0){
            kwargs.filters = filters;
        }
        if(exportOption == "page"){
            kwargs.paginate = [page, pageSize];
        }
        else if(exportOption == "selection"){
            kwargs.filters = [['id','in',getSelectedIds()]];
        }
        call(model, "export", args, kwargs).then(
            (resp) => {
                let requestToken = resp.token;
                downloadReport(requestToken);
            }
        )
    }
</script>

<div>
    <div>
        Export:
        <select class="form-control" bind:value={exportOption}>
            <option value="page">Current page</option>
            <option value="all">All pages</option>
            <option value="selection">Selection</option>
        </select>
    </div>
    <select multiple class="form-control" size="10" bind:value={selectedFields}>
        {#each allFields as field}
            <option value="{field.name}">
                {field.verbose_name}
            </option>
        {/each}
    </select>
    <div style="text-align:center">
        <button type="button" class="btn btn-primary" on:click={doExport}>
            <img src="icons/check2.svg" style="filter:invert(1)" title="Export" alt="Export">
        </button>
    </div>
</div>

<style>
</style>


