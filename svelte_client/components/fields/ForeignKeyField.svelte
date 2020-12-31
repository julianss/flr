<script>
    import { call } from "../../services/service.js"
    import{ fade } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let model = "";
    export let filters = [];
    export let value;
    export let edit;
    export let relatedFields = [];
    export let placeholder = "";
    export let query = "";
    export let readonly;
    let loaded = false;
    let results = [];
    let showResults = false;
    let selectedName = "";
    let uniqueId = Date.now().toString() + "-" + Math.random().toString().substring(2);
    let offset = -1;

    function search(){
        let kwargs = {paginate:[1,10]};
        if(filters.length > 0){
            kwargs.filters = filters;
        }else{
            kwargs.filters = [];
        }
        if(query){
            kwargs.filters.push(['name','ilike',query])
        }
        loaded = false;
        let readFields;
        if(!relatedFields || relatedFields.length == 0){
            readFields = ["id", "name"];
        }else{
            readFields = [];
            for(let rf of relatedFields){
                readFields.push(rf.field);
            }
        }
        //Will throw an error if the model has no regular field called "name"
        //(i.e. if there's no name or if it is a property)
        call(model, "read", [readFields], kwargs).then(
            (resp) => {
                results = resp
                loaded = true;
                offset = -1;
            }
        )
        showResults = true;
    }

    function selectResult(result){
        query = "";
        value = result;
        results = [];
        hideResults();
        dispatch('change', result);
        //document.getElementById("modal-close-"+uniqueId).click()
    }

    function clear(){
        query = "";
        value = false;
        results = [];
        hideResults();
        dispatch('change', false);
    }

    function getSelectedDisplayName(){
        if(typeof(value)==="number"){
            return selectedName;
        }else if(value){
            return value.name || model + "," + value.id;
        }else{
            return ""
        }
    }

    function hideResults() {
        showResults = false;
    }

    // function modalOpen(){
    //     search();
    // }

    document.addEventListener('keydown', function(event){
        var divResults = document.getElementById(`results-dropdown-${uniqueId}`)
        if (divResults && results.length > 0){
            if (event.key === "ArrowDown"){
                if (offset + 1 < divResults.childNodes.length - 1){
                    offset ++;
                }
            }else if (event.key === "ArrowUp"){
                if (offset >= 0){
                    offset --;
                }
                if (offset == -1){
                    hideResults()
                }
            }
            else if (event.key === "Escape"){
                hideResults();
            }
            if (offset >= 0){
                divResults.childNodes[offset].focus()
                if (event.key === "Enter"){
                    selectResult(results[offset])
                }
            }
        }
    })
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && !readonly}
        <div class="input-wrapper">
            <div class="input-group mb-3">
                <input
                    type="text"
                    class="form-control"
                    id="query-input-{uniqueId}"
                    bind:value={query}
                    on:keyup={search}
                    placeholder={placeholder}
                >
                <div class="input-group-append">
                    <button
                        class="btn btn-outline-secondary"
                        on:click={search}
                        type="button"
                        >
                        <img src="icons/caret-down-fill.svg" alt="v"/>
                    </button>
                    <button
                        class="btn btn-outline-secondary"
                        on:click={clear}
                        type="button"
                        >
                        <img src="icons/trash-fill.svg" alt="v"/>
                    </button>
                   <!--<button
                        data-target="#modal-foreignfield-{uniqueId}"
                        on:click={modalOpen}
                        class="btn btn-outline-secondary"
                        type="button">
                        <img src="icons/search.svg" alt="Buscar"/>
                    </button>-->
                </div>
            </div>
            {#if showResults}
                <div
                    id="results-dropdown-{uniqueId}"
                    transition:fade
                    class="dropdown-search-results">
                    {#each results as result}
                        <p tabindex="0" on:click={()=>selectResult(result)}>{result.name}</p>
                    {/each}
                    {#if results.length == 0}
                        <p class="p_sin_resultados">Sin resultados qué mostrar</p>
                    {/if}
                </div>
            {/if}
        </div>
    {:else}
        <p>{value && (value.name || value.id) || ''}</p>
    {/if}
</div>

<!--<div class="modal fade" id="modal-foreignfield-{uniqueId}" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Seleccionar {label}</h5>
        <button id="modal-close-{uniqueId}" type="button" class="close" data-dismiss="modal" aria-label="Cerrar">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <table class="results table table-sm">
            {#if results.length == 0}
                <caption>No se encontraron registros</caption>
            {:else}
                <thead class="thead-light">
                    <tr>
                        <th>{label}</th>
                    </tr>
                </thead>
                <tbody>
                    {#each results as result}
                    <tr on:click={()=>selectResult(result)}>
                        <td>{result.name || model + "," + result.id}</td>
                    </tr>
                    {/each}
                </tbody>
            {/if}
        </table>
      </div>
    </div>
  </div>
</div>-->

<style>
    .input-wrapper{
        position: relative;
    }
    /* .results tr{
        cursor: pointer
    } */
    .dropdown-search-results{
        background-color:white;
        box-shadow: 0px 5px 5px 0px #cccccc;
        border: 1px solid lightgray;
        border-radius: 3px;
        padding: 5px 5px 5px 5px;
        position:absolute;
        margin-top:0px;
        display:block;
        top:32px;
        z-index:2;
        width:100%
    }
    .dropdown-search-results p{
        cursor:pointer;
        margin-top:0px;
        margin-bottom:0px;
        padding: 2px 2px 2px 2px
    }
    .dropdown-search-results p:hover{
        background-color: lightgray
    }
    .p_sin_resultados{
        color:gray;
        font-style: italic
    }
</style>