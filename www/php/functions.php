<?php

    // Para depurar https://www.ibm.com/developerworks/library/os-debug/index.html

    // Este código PHP reside localmente en el server y no es visible desde el navegador.
    // Este PHP será cargado por Apache (si tiene enabled el php_mod),
    // entonces el server atenderá HTTP_REQUEST, y se devolverán resultados
    // mediante el 'echo' final.

    // Definimos 'command' como el argumento que va a recibir este script PHP server side
    // mediaente las HttpRequest originadas por el código javascript cliente, que es 
    // cargado en el navegador (forma parte del http de la peich)
    $command = $_REQUEST["command"];

    // Inicializamos la variable para devolver resultados ante una request
    $result = null;

    // Función que dialoga con el server TCP/IP de PRE.DI.C
    function predic_socket ($cosa) {
        $service_port = 9999;
        $address = "127.0.0.1";
        /* Crear un socket TCP/IP. */
        $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        if ($socket === false) {
            echo "socket_create() falló: razón: " . socket_strerror(socket_last_error()) . "\n";
        }
        $result = socket_connect($socket, $address, $service_port);
        if ($result === false) {
            echo "socket_connect() falló.\nRazón: ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
        }
        socket_write($socket, $cosa, strlen($cosa));
        $out = socket_read($socket, 4096);
        socket_write($socket, "close", strlen("close"));
        socket_read($socket, 4096);
        socket_close($socket);
        return $out;
    }

    // Lee el archivo inputs.yml tal cual
    $inputs_file = "/home/predic/config/inputs.yml";
    function predic_inputs() {
        return readfile("/home/predic/config/inputs.yml"); // no funciona readfile($inputs_file); ¿!?
    }

    if ( $command == "read_inputs_file" ) {
        $result = predic_inputs();
    }
    else {
        $result = predic_socket($command);
    }
        
    // PHP devuelve resultados mediante 'echo xxxxx'
    echo $result;
    
?>

