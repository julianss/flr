<script>
    import { auth } from '../services/service.js';
    let login;
    let password;
    let incorrect = false;
    function authenticate(){
        auth(login, password).then(
            (resp) => {
                if(resp.error){
                    incorrect = true;
                }else{
                    incorrect = false;
                }
            },
        )
    }
</script>

<div id="login-screen">
    <div id="parent">
        <div id="child">
            <img src="/images/logo.svg" id="applogo" alt="App Logo"/>
            <form>
                <div class="form-group">
                    <label>Usuario</label>
                    <input class="form-control" type="text" bind:value={login}>
                </div>
                <div class="form-group">
                    <label>Contraseña</label>
                    <input class="form-control" type="password" bind:value={password}>
                </div>
                <div hidden={!incorrect} class="alert alert-dismissible alert-danger">
                    <button type="button" class="close" data-dismiss="alert">×</button>
                    Usuario o contraseña incorrectos
                </div>
                <button type="button" class="btn btn-primary" on:click={authenticate}>Iniciar sesión</button>
            </form>
        </div>
    </div>
</div>

<style>
    #parent {
        width: 100%;
        height: 50vh;
        display: flex;
        padding: 20px;
        align-items: center;
        justify-content: center;
    }
    #child {
        border-radius: 10px 10px 10px 10px;
        background: #fff;
        width: 90%;
        max-width: 450px;
        position: relative;
        padding: 20px 20px 20px 20px;
        box-shadow: 0 30px 60px 0 rgba(0,0,0,0.3);
        text-align: center;
        margin: auto 0;
    }
    #applogo {
        width: 200px;
        margin-bottom:30px;
    }
</style>
