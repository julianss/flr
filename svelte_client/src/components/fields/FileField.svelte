<script>
    import { createEventDispatcher } from 'svelte';
    import { downloadFile } from '../../services/files.js';
    const dispatch = createEventDispatcher();
    export let label = "";
    export let value;
    export let edit;
    export let readonly;
    let files;

    function changed(){
        var fr = new FileReader();
        fr.onloadend = (res) => {
            var data = res.target.result;
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
    }
</script>

<div class="form-group">
    <label>{label}</label>
    {#if edit && !readonly}
        <div>
            {value && (value.name || '') || ''}
            <img
                hidden={!value || !value.name}
                class="boton"
                on:click={clear}
                src="icons/trash-fill.svg"
                alt="Limpiar campo"/>
            <br/>
            <input type="file" bind:files on:change={changed}/>
        </div>
    {:else}
        <div>
            {#if value && value.id}
                {value.name || ''}
                <img
                    class="boton"
                    on:click={download}
                    src="icons/download.svg"
                    alt="Descargar"/>
            {/if}
        </div>
    {/if}
</div>

<style>
    .boton{
        cursor:pointer
    }
</style>