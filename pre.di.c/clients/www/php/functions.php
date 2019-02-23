<?php

    /*
    Copyright (c) 2018 Rafael Sánchez
    This file is part of pre.di.c
    pre.di.c, a preamp and digital crossover
    Copyright (C) 2018 Roberto Ripio
    pre.di.c is based on FIRtro https://github.com/AudioHumLab/FIRtro
    Copyright (c) 2006-2011 Roberto Ripio
    Copyright (c) 2011-2016 Alberto Miguélez
    Copyright (c) 2016-2018 Rafael Sánchez
    pre.di.c is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    pre.di.c is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with pre.di.c.  If not, see https://www.gnu.org/licenses/.
    */

    /*  This is the hidden server side php code.
        PHP will response to the client via the standard php output, for instance:
            echo $some_varible;
            echo "some_string";
            readfile("some_file_path");
    */

    /////////////////////////////////////////////////////////////////////    
    // GLOBAL VARIABLES:
    $HOME = get_home();
    $CFG_FOLDER = $HOME.'/pre.di.c/config';
    $MACROS_FOLDER = $HOME.'/pre.di.c/clients/www/macros';
    $LSPKNAME = get_config('loudspeaker');
    $LSPK_FOLDER = $HOME.'/pre.di.c/loudspeakers/'.$LSPKNAME;
    /////////////////////////////////////////////////////////////////////

    // use only to cmdline debugging
    //echo '---'.$HOME.'---';
    //echo '---'.$CFG_FOLDER.'---';
    //echo '---'.$LSPKNAME.'---';
    //echo '---'.$LSPK_FOLDER.'---';

    // Gets the base folder where php code and pre.di.c are located
    function get_home() {
        $phpdir = getcwd();
        $pos = strpos($phpdir, 'pre.di.c');
        return substr($phpdir, 0, $pos-1 );
    }

    // Gets the directory list of files inside the loudspeker folder
    function dir_lspk_folder() {
        // to have access to variables outside
        global $LSPK_FOLDER;
        return json_encode( scandir( $LSPK_FOLDER ) );
    }

    // Gets single line configured items from pre.di.c 'config.yml' file
    function get_config($item) {
        // to have access to variables outside
        global $CFG_FOLDER;

        //$filepath = $CFG_FOLDER."/config.yml";
        $tmp = "";
        $cfile = fopen( $CFG_FOLDER."/config.yml", "r" )
                  or die("Unable to open file!");
        while( !feof($cfile) ) {
            $linea = fgets($cfile);
            // Ignore yaml commented out lines
            if ( strpos($linea, '#') === false ) {
                if ( strpos( $linea, $item) !== false ) {
                    $tmp = str_replace( "\n", "", $linea);
                    $tmp = str_replace( $item, "", $tmp);
                    $tmp = str_replace( ":", "", $tmp);
                    $tmp = trim($tmp);
                }
            }
        }
        fclose($cfile);
        return $tmp;
    }

    // Communicates to the pre.di.c TCP/IP servers.
    // Notice: server address and port are specified
    //         into 'config/config.yml' for each service,
    //         for instance 'control', 'players' or 'aux'.
    function predic_socket ($service, $cmd) {
    
        $address = get_config( $service."_address" );
        $port    = intval( get_config( $service."_port" ) );
        
        // Creates a TCP socket
        $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        if ($socket === false) {
            echo "socket_create() failed: " . socket_strerror(socket_last_error()) . "\n";
        }
        $result = socket_connect($socket, $address, $port);
        if ($result === false) {
            echo "socket_connect() failed: ($result) " . socket_strerror(socket_last_error($socket)) . "\n";
        }
        // Sends and receive:
        socket_write($socket, $cmd, strlen($cmd));
        $out = socket_read($socket, 4096);
        // Tells the server to close the connection from its end:
        socket_write($socket, "quit", strlen("quit"));
        // Empties the receiving buffer:
        socket_read($socket, 4096);
        // And close this end socket:
        socket_close($socket);
        return $out;
    }

    ///////////////////////////   MAIN: ///////////////////////////////
    // listen to http request then returns results via standard output

    /*  http://php.net/manual/en/reserved.variables.request.php
        PHP server side receives associative arrays, i.e. dictionaries, through by the 
        GET o PUT methods from the client side HTTPREQUEST (usually javascript).
        The array is what appears after 'php/functions.php?.......', example:
                "GET", "php/functions.php?command=level -15"
        Here the key 'command' has the value 'level -15'
        So, lets read the key 'command', then run corresponding actions:
    */
    $command = $_REQUEST["command"];

    // READING LOUDSPEAKER DIR FILES
    if ( substr( $command, 0, 15 ) === "dir_lspk_folder" ) {
        echo dir_lspk_folder();
    }

    // READING THE LOUDSPEAKER NAME:
    elseif ( $command == "get_loudspeaker_name" ) {
        echo get_config("loudspeaker");
    }

    // UPLOADING SOME FILES: inputs.yml, config.yml, speaker.yml, .loudness_monitor
    // Notice: readfile() does an 'echo', so it returns the contents to the standard php output
    elseif ( $command == "read_inputs_file" ) {
        readfile($CFG_FOLDER."/inputs.yml");
    }
    elseif ( $command == "read_config_file" ) {
        readfile($CFG_FOLDER."/config.yml");
    }
    elseif ( $command == "read_speaker_file" ) {
        $fpath = $LSPK_FOLDER."/speaker.yml";
        readfile($fpath);
    }
    elseif ( $command == "read_loudness_monitor_file" ) {
        $fpath = $HOME."/pre.di.c/.loudness_monitor";
        readfile($fpath);
    }
    
    // AUX commands are handled by the 'aux' server

    // Aux: AMPLIFIER
    // Notice: It is expected that the remote script will store the amplifier state
    //         into the file '~/.amplifier' so that the web can update it.
    elseif ( $command == "amp_on" ) {
        predic_socket( 'aux', 'amp_on');
    }
    elseif ( $command == "amp_off" ) {
        predic_socket( 'aux', 'amp_off');
    }
    elseif ( $command == "amp_state" ) {
        readfile($HOME."/.amplifier"); // php cannot acces inside /tmp for securety reasons.
    }

    // Aux: LOUDNESS MONITOR RESET
    elseif ( $command == "loudness_monitor_reset" ) {
        predic_socket( 'aux', $command );
    }

    // Aux: TARGET change
    elseif ( substr( $command, 0, 10 ) === "set_target" ) {
        predic_socket( 'aux', $command );
    }

    // Aux: USER MACROS
    elseif ( substr( $command, 0, 6 ) === "macro_" ) {
        echo predic_socket( 'aux', $command );
    }
    elseif ( $command === "list_macros" ) {
        $macros_array = scandir($MACROS_FOLDER."/");
        echo json_encode( $macros_array );
    }

    // PLAYERS related commands are handled by the 'players' server
    elseif ( substr( $command, 0, 7 ) === "player_" ) {
        // The expected playback control syntax is: 'player_play', 'player_pause', etc
        echo predic_socket( 'players', $command );
    }
    elseif ( substr( $command, 0, 4 ) === "http" ) {
        // A stream url to be played back
        echo predic_socket( 'players', $command );
    }

    // PRE.DI.C: any else will be an STANDARD pre.di.c CONTROL command, handled by the 'control' server
    else {
        echo predic_socket( 'control', $command );
    }

?>
