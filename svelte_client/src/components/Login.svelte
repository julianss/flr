<script>
    import { auth, recoverypassword, resetPassword } from '../services/service.js';
    let login;
    let password;
    let incorrect = false;
    let recoveryscreen = false;
    let email;
    let send_message = false;
    let resetpassword = false;
    let token;
    let newpassword = "";
    let confirmpass = "";
    let successreset = false;
    $:{
        if (window.location.pathname === '/resetPassword'){
            resetpassword = true;
        }
    }
    function authenticate(event){
        if (!(event.key === 'Enter' || event.type==='click')){
           return
        }
        auth(login, password).then(
            (resp) => {
                if(resp.error){
                    incorrect = 'Usuario o contraseña incorrectos';
                }else{
                    incorrect = false;
                }
            },
        )
    }
    function recoveryScreen(){
        recoveryscreen = true
    }
    function recoveryPassword(){
        recoverypassword(email).then((resp)=> {
            if (!resp.error){
                send_message = true;
                incorrect = false;
            }else{
                incorrect = resp.error.message;
            }
        })
    }
    function doResetPassword(){
        if ((newpassword.length == 0)||(confirmpass.length == 0)){
            incorrect = 'Llene los campos de las contraseñas'
        }else{
            if (newpassword === confirmpass){
                resetPassword(confirmpass).then((resp) => {
                    if (!resp.error){
                        successreset = true;
                    }else{
                        successreset = false;
                    }
                })
            }
            else{
                incorrect = 'No coinciden las contraseñas'
            }
        }
    }

    function authscreen(){
        resetpassword = false;
        history.pushState(null, null, '/#')
    }

    function resetAlert(){
        incorrect = false;
    }

    function setInputType(inputId, imgId){
        var inputObj = document.getElementById(inputId);
        if (inputObj){
            var buttonImg = document.getElementById(imgId)
            if (inputObj.type === "password"){
                inputObj.type = "text";
                buttonImg.src = "icons/eye-slash.svg"
            }else{
                inputObj.type = "password";
                buttonImg.src = "icons/eye.svg"
            }
            inputObj.focus()
        }
    }

</script>

<div id="login-screen">
    <div id="parent">
        <div id="child">
            <img src="/images/logo.png" id="applogo" alt="App Logo"/>
            <form>
                {#if incorrect}
                    <div class="alert alert-dismissible alert-danger">
                        <button type="button" class="close" data-dismiss="alert"
                            on:click={resetAlert}>×</button>
                        {incorrect}
                    </div>
                {/if}
                {#if !resetpassword}
                    {#if !recoveryscreen}
                        <div class="form-group">
                            <label>Usuario</label>
                            <input class="form-control" type="text" bind:value={login}>
                        </div>
                        <div class="form-group">
                            <label>Contraseña</label>
                            <div class="input-group">
                                <input class="form-control border-right-0" id="password" type="password"
                                    bind:value={password}
                                    on:keyup={authenticate}>
                                <div class="input-group-prepend border-right-0">
                                    <button tabindex="-1" type="button" class="btn border border-left-0 pb-1"
                                        on:click={() => setInputType("password", "passwordimg")}>
                                        <img
                                            id="passwordimg"
                                            src="icons/eye.svg"
                                            alt="Show"
                                        />
                                    </button>
                                </div>
                            </div>

                        </div>
                        <div class="form-group">
                            <button type="button" class="btn btn-primary" on:click={authenticate}>Iniciar sesión</button>
                        </div>
                        <div class="form-group">
                            <a class="text-primary" href="#" on:click={recoveryScreen}>Olvidé mi contraseña</a>
                        </div>
                    {:else}
                        {#if !send_message}
                            <div class="form-group">
                                <label>Ingresa tu email para reestablecer tu contraseña</label>
                                <input class="form-control" type="text" bind:value={email}>
                            </div>
                            <button type="button" class="btn btn-primary" on:click={recoveryPassword}>Enviar</button>
                        {:else}
                            <div class="form-group">
                                <label>Se ha enviado un correo a {email}</label>
                            </div>
                        {/if}
                    {/if}
                {:else}
                    {#if !successreset}

                        <div class="form-group">
                            <label>Nueva contraseña</label>
                            <div class="input-group">
                                <input class="form-control border-right-0" id="newpassword" type="password" bind:value={newpassword}>
                                <div class="input-group-prepend border-right-0">
                                    <button tabindex="-1" type="button" class="btn border border-left-0 pb-1"
                                        on:click={() => setInputType("newpassword", "newpasswordimg")}>
                                        <img
                                            id="newpasswordimg"
                                            src="icons/eye.svg"
                                            alt="Show"
                                        />
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Confirmar contraseña</label>
                            <div class="input-group">
                                <input class="form-control border-right-0" id="confirmpass" type="password" bind:value={confirmpass}>
                                <div class="input-group-prepend border-right-0">
                                    <button tabindex="-1" type="button" class="btn border border-left-0 pb-1"
                                        on:click={() => setInputType("confirmpass", "confirmpassimg")}>
                                        <img
                                            id="confirmpassimg"
                                            src="icons/eye.svg"
                                            alt="Show"
                                        />
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <button type="button" class="btn btn-primary" on:click={doResetPassword}>Cambiar contraseña</button>
                        </div>
                    {:else}
                        <div class="form-group">
                            <label>Se ha cambiado la contraseña con éxito</label>
                        </div>
                        <div class="form-group">
                            <button type="button" class="btn btn-primary" on:click={authscreen}>Iniciar sesión</button>
                        </div>
                    {/if}
                {/if}
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
