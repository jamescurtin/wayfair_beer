import {
    autocomplete
} from './autocomplete.js';

/**
 * Toggle the kicked flag on each tapped beer to change the display status on
 * the dashboard
*/
function toggle_kicked_keg() {
    var button = $(".kicked-button")
    button.click(function() {
        var buttonid = $(this).attr("id")
        var ontap_id = buttonid.split("-").pop();
        $.ajax({
            url: "/update_kicked_beer"
            , type: "POST"
            , dataType: "json"
            , data: {
                "ontap_id": ontap_id
            }
        }).done(function(beers) {
            window.location.reload();
        });
    });
}

/**
 * Record the star rating when a beer is rated
*/
function record_rating() {
    var rating = $(".star")
    rating.click(function() {
        var clicked = $(this).attr('id')
        var clicked_elements = clicked.split("-")
        $.post("/record_rating", {
            ontap_id: clicked_elements[0]
            , rating: clicked_elements[1]
        });
        $('#success-modal').modal('show')
        setTimeout(function() {
            $('#success-modal').modal('hide')
        }, 1500);
    })
}

/**
 * Populate the autocomplete fields for brewery/beer name when tapping new
 * beers
*/
function autocomplete_adding_beer() {
    $.ajax({
        url: "/get_breweries"
        , type: "POST"
        , dataType: "json"
        , data: {}
    }).done(function(breweries) {
        autocomplete(document.getElementById("brewery_input"), breweries);
    });
    $.ajax({
        url: "/get_beers"
        , type: "POST"
        , dataType: "json"
        , data: {}
    }).done(function(beers) {
        autocomplete(document.getElementById("beer_input"), beers);
    });
}

/**
 * Update the beer displayed on the tap dashboard when a new beer has been
 * tapped
*/
function update_beer() {
    $(".select-beer").click(function() {
        var this_id_attrs = $(this).attr("id").split('-')
        var tap_id = this_id_attrs.pop();
        var beer_id = this_id_attrs.pop();
        $.ajax({
            url: "/confirm_tapped_beer"
            , type: "POST"
            , dataType: "json"
            , data: {
                "tap_id": tap_id
                , "beer_id": beer_id
            }
        }).done(function(beers) {
            window.location.reload();
        });
    })
}

/**
 * Add a new beer to the database if it cannot be found in the Untappd database
*/
function manually_enter_beer(form_data) {
    $("#select_tapped_beer_close").click(function() {
        $("#beer-options").empty();
    })
    $(".new-selected-beer-none").click(function() {
        var this_id_attrs = $(this).attr("id").split('-')
        var tap_id = this_id_attrs.pop();
        $.ajax({
            url: "/confirm_tapped_beer"
            , type: "POST"
            , dataType: "json"
            , data: {
                "tap_id": tap_id
                , "beer_id": 1
            }
        }).done(function(beers) {
            window.location.reload();
        });
    })
}


function clear_modals() {
    $("#close_tap_beer").click(function() {
        $("#beer-options").empty();
    })
    $("#close_search_beer").click(function() {
        $("#tap_new_beer").reset();
    })
};

function select_beer_to_tap(json, form_data) {
    var beer_option_div = $("#beer-options");
    var option_table = $("<table></table>");
    var beer_status = $("#status-beer");
    beer_status.show();
    $("<tr><th>Brewery</th><th>Beer</th><th>Image</th><th></th></tr>").appendTo(option_table);
    var tap_id = json['tap_id'];
    $.each(json['beers'], function(index, beer) {
        var beer_row = $('<tr></tr>')
        var beer_data = $(
            `
            <td>${beer['brewery']['name']}</td>
            <td>${beer['name']}</td>
            <td><img src="/static/img/labels/${beer['image']}" height="100px"></td>
            <td><button id="new-selected-beer-${beer['id']}-${tap_id}" class="btn btn-success select-beer" >Select</button></td>
            `
        )
        beer_data.appendTo(beer_row);
        beer_row.appendTo(option_table);
    });
    if (json['beers'].length > 0) {
        $(
            `
           <tr>
               <td></td>
               <td></td>
               <td></td>
               <td><button class="new-selected-beer-none" id="new-selected-beer-none-${tap_id}" class="btn btn-warning" >None of the above</button></td>
           `
        ).appendTo(option_table)
    } else {
        option_table.empty()
        $(
            `<button class="new-selected-beer-none" id="new-selected-beer-none-${tap_id}" class="btn btn-warning" >No match found: Click here</button>`
        ).appendTo(beer_option_div)
    }
    option_table.appendTo(beer_option_div);
    beer_status.hide();
    manually_enter_beer(form_data);
    update_beer();
    $('#tap_new_beer_modal').modal('hide');
    $("#select_tapped_beer").modal('show');
};

function close_modal_on_submit() {
    $('#tap_new_beer').submit(function(e) {
        var form_data = $("#tap_new_beer").serialize()
        $.ajax({
            type: "POST"
            , url: "/tap_new_beer"
            , dataType: "json"
            , data: form_data
        }).done(function(json) {
            select_beer_to_tap(json, form_data);
        });
        $('#tap_new_beer_modal').modal('hide');
        $('#tap_new_beer').trigger("reset");
        e.preventDefault();
        $('#select_tapped_beer').modal('show');
    });
}

$('#tap_new_beer_modal').on('show.bs.modal', function(e) {
    var button_id = $(e.relatedTarget).attr('id')
    var tap_id = button_id.split("-").pop()
    $("#form_tap_id").val(tap_id)
})

function resize_main_container() {
    var $header = $('.navbar');
    var $footer = $('#footer');
    var $content = $('#content');
    var $window = $(window).on('resize', function() {
        var height = $(this).height() - $header.height() + $footer.height();
        $content.height(height);
    }).trigger('resize');
};

$(document).ready(function() {
    $("#body").css("min-height", screen.height);
    resize_main_container();
    toggle_kicked_keg();
    record_rating();
    autocomplete_adding_beer();
    close_modal_on_submit();
    clear_modals();
});
