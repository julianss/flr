<script>
    export let label = "";
    export let value;
    export let edit;
</script>

<div class="form-check">
    <input class="form-check-input" type="checkbox" bind:checked={value} disabled={!edit}/>
    <label class="form-check-label">{label}</label>
</div>