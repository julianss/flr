<script>
	import Login from './components/Login.svelte';
	import Loader from './components/Loader.svelte';
	import Navbar from './components/Navbar.svelte';
	import WorkArea from './components/WorkArea.svelte';
	import { jwt } from './services/service.js'
	let logged = false;
	jwt.subscribe((value)=>{
		if(value != ''){
			logged = true;
		}
	})
</script>

<Loader/>

{#if logged }
	<Navbar/>
	<WorkArea/>
{:else}
	<Login/>
{/if}