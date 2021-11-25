<script>
    import { createEventDispatcher } from 'svelte';
    import { downloadFile, getSrcWithToken } from '../../services/files.js';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    export let options;
    export let viewtype;
    let files;
    let preview;

    function changed(){
        var fr = new FileReader();
        fr.onloadend = (res) => {
            var data = res.target.result;
            preview = data
            data = data.split(",")[1];
            if(!value){
                value = {};
            }
            value.datab64 = data;
            value.name = files[0].name;
        }
        fr.readAsDataURL(files[0]);
        dispatch("change", {});
    }

    function download(){
        downloadFile(value.id);
    }

    function clear() {
        value = null;
        preview = null;
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if viewtype === 'form'}
        {#if edit && !readonly}
            <div>
                {#if (preview || value && value.id) && options && options.image === true}
                    <img
                        class="preview"
                        src={preview || getSrcWithToken(value.id)}
                        alt={value && (value.name || '') || ''}
                        title={value.name || ''}
                        />
                {:else}
                    {value && (value.name || '') || ''}
                {/if}
                <button class="btn btn-info"
                    on:click={clear}
                    hidden={!value || !value.name}
                    >
                        <img
                            style="filter:invert(1)"
                            src="icons/trash-fill.svg"
                            alt="Limpiar campo"/>
                </button>
                <br/>
                <input type="file" bind:files on:change={changed}/>
            </div>
        {:else}
            <div>
                {#if value && value.id}
                    {#if !value.datab64 && options && options.image === true}
                        <img
                            class="preview"
                            src={getSrcWithToken(value.id)}
                            alt={value && (value.name || '') || ''}
                            title={value.name || ''}/>
                    {/if}
                    <button class="btn btn-info"
                        on:click={download}>
                            <img
                                style="filter:invert(1)"
                                src="icons/download.svg"
                                alt="Descargar"/>
                    </button>
                {/if}
            </div>
        {/if}
    {/if}
</div>

<style>
    .boton{
        cursor:pointer
    }
    .preview{
        max-width:120px;
    }
</style>