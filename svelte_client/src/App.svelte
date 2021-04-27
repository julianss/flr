<script>
	import { addMessages, init, getLocaleFromNavigator, locale } from 'svelte-i18n';
	import en from './i18n/en.json';
	import es from './i18n/es.json';
	addMessages('en', en);
	addMessages('es', es);
	init({
	  	fallbackLocale: 'en',
  		initialLocale: getLocaleFromNavigator(),
	});

	import Login from './components/Login.svelte';
	import Loader from './components/Loader.svelte';
	import Navbar from './components/Navbar.svelte';
	import WorkArea from './components/WorkArea.svelte';
	import { call, jwt, JWT_NOT_YET_LOADED } from './services/service.js'
	let logged = false;
	let showApp = false;
	jwt.subscribe((value)=>{
	  if(value !== JWT_NOT_YET_LOADED && value != ''){
		logged = true;
	  }
	  if(value !== JWT_NOT_YET_LOADED){
		showApp = true;
		call("FlrUser", "get_lang").then((resp) => locale.set(resp));
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