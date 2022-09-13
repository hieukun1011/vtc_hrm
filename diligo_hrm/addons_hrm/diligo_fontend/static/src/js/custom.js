odoo.define('diligo_fontend.custom', function (require) {
'use strict';
require('web.dom_ready');
var rpc = require('web.rpc');
var ajax = require('web.ajax');
$(document).ready(function(){

   $('#sl_state').change(function(event){
        // Check input( $( this ).val() ) for validity here
        // alert($(this).val());

        var data = $('#sl_state').val();

        var state_id = $(this).val();


        rpc.query({
                route: "/apply-distributors/state/" + state_id,
            }).then(function (data) {
                $('#district').html('');

                // Fill data vao district
                for (const [key, value] of Object.entries(data)) {

                  var opt = $('<option>').text(value)
                   .attr('value', key);
                   $('#district').append(opt);
                }
            });

        $('#district').change(function(event){
            // Check input( $( this ).val() ) for validity here
            // alert($(this).val());

            var data = $('#district').val();
            var district_id = $(this).val();


            rpc.query({
                    route: "/apply-distributors/district/" + district_id,
                }).then(function (data) {
                    $('#sl_wards').html('');

                    // Fill data vao district
                    for (const [key, value] of Object.entries(data)) {

                      var opt = $('<option>').text(value)
                       .attr('value', key);
                       $('#sl_wards').append(opt);
                    }
                });
            $('#sl_wards').change(function(event){

                var state = $('#sl_state option:selected').text().trim();
                var district = $('#district option:selected').text().trim();
                var wards = $('#sl_wards option:selected').text().trim();

                var emergency_contact = '';
                if(wards){
                    emergency_contact += wards + ', ';
                }
                if(district){
                    emergency_contact += district + ', ';
                }
                if(state){
                    emergency_contact += state;
                }


                $('#emergency_contact').val(emergency_contact);
            });
        });





    });



  })


});
