<script>
	import Login from './components/Login.svelte';
	import Loader from './components/Loader.svelte';
	import Navbar from './components/Navbar.svelte';
	import WorkArea from './components/WorkArea.svelte';
	import { jwt, JWT_NOT_YET_LOADED } from './services/service.js'
	let logged = false;
	let showApp = false;
	jwt.subscribe((value)=>{
	  if(value !== JWT_NOT_YET_LOADED && value != ''){
		logged = true;
	  }
	  if(value !== JWT_NOT_YET_LOADED){
		showApp = true;
	  }
	})
  </script>
  
  <Loader/>
  
  {#if showApp}
	{#if logged }
		<Navbar/>
		<WorkArea/>
	{:else}
		<Login/>
	{/if}
  {/if}