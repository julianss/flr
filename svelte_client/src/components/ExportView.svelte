<script>
    import { call, importData } from '../services/service.js';
    import { downloadReport } from '../services/report.js';
    import { fade } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let model;
    export let selectedFields = [];
    export let filters = [];
    export let page;
    export let pageSize;
    export let selectedRecords;
    let exportOption = "current";
    let allFields = [];
    let filesToImport;
    let importErrors;
    let importOk = false;
    $: {
        if(model){
            call(model, "get_fields", {with_verbose_name:true}).then(
                (resp) => {
                    allFields = resp;
                    importErrors = false;
                    clearFile();   
                }
            )
        }
    }

    function clearFile() {
        filesToImport = '';
        document.getElementById("file-to-import").value = '';
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

    function doImport() {
        if(!filesToImport){
            return;
        }
        importOk = false;
        importErrors = false;
        let file = filesToImport[0];
        let fields = selectedFields.join(",");
        importData(model, fields, file).then(
            (resp) => {
                if(resp.$error){
                    importErrors = resp.$error.message.replace(/\n/g, "<br/>");
                    clearFile();
                }else{
                    importOk = true;
                    setTimeout(()=>{
                        importOk = false;
                    }, 2500);
                    dispatch('success', {});
                    clearFile();
                }
            }
        )
    }
</script>

<div>
    <div>
        <select multiple class="form-control" size="10" bind:value={selectedFields}>
            {#each allFields as field}
                <option value="{field.name}">
                    {field.verbose_name}
                </option>
            {/each}
        </select>
    </div>
    <hr/>
    <div>
        <h3>Export:</h3>
        <select class="form-control" bind:value={exportOption}>
            <option value="page">Current page</option>
            <option value="all">All pages</option>
            <option value="selection">Selection</option>
        </select>
    </div>
    <div style="text-align:center">
        <button type="button" class="btn btn-primary" on:click={doExport}>
            <img src="icons/check2.svg" style="filter:invert(1)" title="Export" alt="Export">Export
        </button>
    </div>
    <hr/>
    <div>
        <h3>Import:</h3>
        <input type="file" bind:files={filesToImport} id="file-to-import"/>
        <div style="text-align:center">
            <button type="button" class="btn btn-primary" on:click={doImport}>
                <img src="icons/check2.svg" style="filter:invert(1)" title="Import" alt="Export">Import
            </button>
        </div>
        <div class="import-errors" hidden={!importErrors}>
            {@html importErrors}
        </div>
        <div class="import-ok" transition:fade hidden={!importOk}>
            Import succesful
        </div>
    </div>
</div>

<style>
    .import-errors{
        padding: 5px 5px 5px 5px;
        background-color: salmon;
        color: rgb(49, 7, 7);
        overflow-y: scroll;
        max-height: 300px
    }
    .import-ok{
        padding: 5px 5px 5px 5px;
        background-color: rgb(221, 255, 221);
        color: green;
    }
</style>


