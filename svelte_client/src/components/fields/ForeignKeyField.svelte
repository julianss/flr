<script>
    import { call } from "../../services/service.js"
    import{ fade } from 'svelte/transition';
    import { createEventDispatcher } from 'svelte';
    import {activeElement} from '../../services/writables.js'
    const dispatch = createEventDispatcher();
    export let label = "";
    export let model = "";
    export let model_name_field = "";
    export let filters = [];
    export let value;
    export let edit;
    export let placeholder = "";
    export let query = "";
    export let readonly;
    export let options;
    let loaded = false;
    let results = [];
    let showResults = false;
    let selectedName = "";
    let uniqueId = Date.now().toString() + "-" + Math.random().toString().substring(2);
    let offset = -1;
    let highlightedResult = -1;
    let inputElement;
    let resultsDropdownElement;

    function caretDownClicked(event) {
        if(showResults){
            hideResults();
        }else{
            inputElement.focus();
            search(event, {doNotFilterInput: true});
        }
    }

    function search(event, opts={}){
        if(event){
            if (["ArrowDown", "ArrowUp", "Escape", "Enter"].includes(event.key)){
                return keyboardNavigation(event);
            }
        }
        activeElement.set(uniqueId)
        let kwargs = {paginate:[1,10]};
        if(filters.length > 0){
            kwargs.filters = [...filters];
        }else{
            kwargs.filters = [];
        }
        if(query && !opts.doNotFilterInput){
            if (options && options.name_field){
                kwargs.filters.push([options.name_field,'ilike',query])
            }else{
                kwargs.filters.push([model_name_field,'ilike',query])
            }
        }
        loaded = false;
        let readFields = ["id"];
        if (options && options.name_field){
            readFields.push(options.name_field)
        }else if(options && options.related_fields){
            readFields = [];
            for(let rf of options.related_fields){
                readFields.push(rf.field);
            }
            readFields = readFields;
        }else{
            readFields.push(model_name_field)
        }
        //Will throw an error if the model has no regular field called "name"
        //(i.e. if there's no name or if it is a property)
        call(model, "read", [readFields], kwargs).then(
            (resp) => {
                results = resp;
                loaded = true;
                offset = -1;
            }
        )
        showResults = true;
    }
    activeElement.subscribe((value) => {
        if(value){
            if (!(value===uniqueId)){
                hideResults()
            };
        }
    });

    function selectResult(result){
        value = result;
        hideResults();
        dispatch('change', result);
        //document.getElementById("modal-close-"+uniqueId).click()
    }

    function onBlur(){
        //The input loses focus and no selection was made, but the user may have written something.
        //Either clear it or revert it to the correct value
        if(!value){
            query = "";
        }else{
            if (options && options.name_field){
                query = value[options.name_field]
            }else{
                query = value[model_name_field]
            }
        }
        hideResults();
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
            if (options && options.name_field){
                return value[options.name_field];
            }else{
                return value[model_name_field] || model + "," + value.id;
            }
        }else{
            return ""
        }
    }

    function hideResults() {
        results = [];
        highlightedResult = -1;
        showResults = false;
    }

    // function modalOpen(){
    //     search();
    // }

    function keyboardNavigation(event){

        if (!showResults && event.key == "ArrowDown") {
            return caretDownClicked();
        }

        var divResults = resultsDropdownElement;
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
                event.preventDefault()
                highlightedResult = offset;
                if (event.key === "Enter"){
                    selectResult(results[offset]);
                    hideResults();
                }
            }
        }else if (divResults && results.length == 0){
            if (event.key === "Escape"){
                hideResults();
            }
        }
    }
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
                    bind:this={inputElement}
                    on:keyup={search}
                    on:blur={onBlur}
                    placeholder={placeholder}
                >
                <div class="input-group-append">
                    <button
                        class="btn btn-outline-secondary"
                        on:click={caretDownClicked}
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
                    bind:this={resultsDropdownElement}
                    transition:fade
                    class="dropdown-search-results">
                    {#each results as result, i}
                        <p class="result" tabindex="0"
                        class:highlight={highlightedResult == i}
                        on:click={()=>selectResult(result)}>{
                            result&&options&&'name_field' in options?result[options.name_field]:
                            result&&options&&'related_fields' in options?
                                options.related_fields.map(item => result[item.field]).join('-'):
                            result[model_name_field]}</p>
                    {/each}
                    {#if results.length == 0}
                        <p class="p_sin_resultados">Sin resultados qué mostrar</p>
                    {/if}
                </div>
            {/if}
        </div>
    {:else}
        {#if options && options.name_field && value}
            <p>{value[options.name_field] || value.id || ''}</p>
        {:else}
            <p>{value && (value[model_name_field] || value.id) || ''}</p>
        {/if}
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
    .highlight {
        background-color: lightgray
    }
</style>