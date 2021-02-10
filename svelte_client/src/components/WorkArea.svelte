<script>
    import ListView from './ListView.svelte';
    import FormView from './FormView.svelte';
    import SearchView from './SearchView.svelte';
</script>

<div id="workarea-container">
    <ListView/>
    <FormView/>
    <SearchView/>
</div>

<style>
    #workarea-container{
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
