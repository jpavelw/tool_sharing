/**
 * Created by Jairo on 09/29/2015.
 */
(function(){
	var app = angular.module('toolReview', []);

	app.config(function($httpProvider) {
	    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
	});

	app.config(function($interpolateProvider) {
	    $interpolateProvider.startSymbol('{$');
	    $interpolateProvider.endSymbol('$}');
	});

	app.controller('ToolController', [ '$http', '$rootScope', function($http, $rootScope){
		var outCtr = this;
        var URL = $( "#url" ).text();

		$http.get(URL).success(function(data){
            if(data.statusCode == 200){
                $rootScope.reviews = JSON.parse(data.data);
                outCtr.reviews = $rootScope.reviews;
            }
		});
	}]);

	app.controller('ReviewController', [ '$http', '$rootScope', function($http, $rootScope){
		var inCTR = this;
        inCTR.review = "";
		inCTR.show = true;

		this.addReview = function(URL){
            var $csrftoken = $('input[name="csrfmiddlewaretoken"]');
            var token = $csrftoken.attr( "value" );
            var request = {
                 method: 'POST',
                 url: URL,
                 headers: {
                   'Content-Type': 'application/x-www-form-urlencoded'
                 },
                 data: $.param({
                     csrfmiddlewaretoken: token,
                     description: inCTR.review.description,
                     user_name: inCTR.review.user_name,
                     rate: inCTR.review.rate,
                     title: inCTR.review.title
                 })
            }
            $http(request).success(function(data){
                if(data.statusCode == 200){
                    $rootScope.reviews.push(JSON.parse(data.data)[0]);
                    inCTR.review = "";
                    inCTR.show = false;
                }
                else{
                    alert(data.message);
                }
            });
		};
	}]);

})();
$(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.document.location = $(this).data("href");
    });
    $( ".msg-alert" ).click();

    $( ".upd_status" ).change(function(event) {
        var select = $(event.target);
        var status_code = select.val().split(",")[0];
        var url = select.val().split(",")[1];

        $.ajax({
            type: "POST",
            dataType: "json",
            url: url,
            data: { status_code: status_code },
            success: function(data) {
                if(data.statusCode == 200){
                    //alert("success - " + data.message);
                }	else {
                    //alert("error not 200 - " + data.message);
                }
            },error: function(data) {
                //alert("error - " + data.message);
            }
        });
    });

    $('#actionModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var tool_id = button.data('requestid');
        var modal = $(this);
        modal.find('#requestid').text(tool_id);
        $('#request-comment').val("");
        $('#modal-footer').removeClass( 'hide' );
        $('#action-alert').removeClass( 'alert-danger' );
        $('#action-alert').removeClass( 'alert' );
        $('#action-alert').addClass( 'hide' );
        $('#action-alert').text("");
    });

    $( ".a-r-request" ).click(function(event) {

        $('#action-alert').removeClass( 'alert-danger' );
        $('#action-alert').removeClass( 'alert' );
        $('#action-alert').addClass( 'hide' );
        $('#action-alert').text("");

        var button = $(event.target);
        var action = button.attr('id');
        var request_id = $('#requestid').text();
        var _url = $('#requestid').data('url');
        var _comment = $('#request-comment').val();

        if(_comment.trim() == ""){
            $('#action-alert').addClass( 'alert-danger' );
            $('#action-alert').addClass( 'alert' );
            $('#action-alert').removeClass( 'hide' );
            $('#action-alert').text("Please provide a comment!");
        }
        else{
            $.ajax({
                type: "POST",
                dataType: "json",
                url: _url,
                data: { request_id: request_id, action:action, comment: _comment },
                success: function(data) {
                    if(data.statusCode == 200){
                        $('#action-alert').addClass( 'alert-success' );
                        $('#action-alert').addClass( 'alert' );
                        $('#action-alert').removeClass( 'hide' );
                        $('#action-alert').text(data.message);
                        $('#modal-footer').addClass( 'hide' );
                        $('#action-' + request_id).text("");
                        $('#status-' + request_id).text(data.status);
                    }	else {
                        $('#action-alert').addClass( 'alert-danger' );
                        $('#action-alert').addClass( 'alert' );
                        $('#action-alert').removeClass( 'hide' );
                        $('#action-alert').text(data.message);
                    }
                },error: function(data) {
                    //alert("error - " + data.message);
                }
            });
        }
    });

    $('#toolDetailModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var _url = button.data('url');
        var _toolid = button.data('toolid');
        $("#request-url").text(_url);
        $("#tool-id").text(_toolid);

        $.ajax({
            type: "GET",
            dataType: "json",
            url: _url,
            data: { format: "json" },
            success: function(data) {
                if(data.statusCode == 200){
                    var _tool = JSON.parse(data.data);
                    $("#tool-img").attr("src", data.media + _tool[0].fields.picture);
                    $("#link-img").attr("href", data.media + _tool[0].fields.picture);
                    $("#tool-img").attr("alt", _tool[0].fields.name);
                    $("#tool-name").text(_tool[0].fields.name);
                    $("#tool-code").text(_tool[0].fields.code);
                    $("#tool-description").text(_tool[0].fields.description);
                    $("#pu-address").text(data.pickup_address);
                    if(data.pickup_times != null){
                        $("#pu-days").text(data.pickup_times.days);
                        $("#pu-hours").text(data.pickup_times.hours);
                    }
                    else{
                        $('#pick-up-time-div').addClass( 'hide' );
                    }
                } else {
                    $('#msg-error').removeClass( 'hide' );
                    $('#row-content').addClass( 'hide' );
                    $('#msg-error').text(data.message);
                }
            },error: function(data) {
                //alert("error - " + data.message);
            }
        });

    });

    $( "#confirm-request" ).click(function() {
        var $csrftoken = $('input[name="csrfmiddlewaretoken"]');
        var _token = $csrftoken.attr( "value" );
        var _url = $("#request-url").text();
        var _tool_id = _url.split('/');


        $.ajax({
            type: "POST",
            dataType: "json",
            url: _url,
            data: { csrfmiddlewaretoken: _token, format: "json" },
            success: function(data) {
                if(data.statusCode == 200){
                    var _toolid = $("#tool-id").text();
                    $('#form-part').addClass( 'hide' );
                    $('#btn-' + _toolid).addClass( 'hide' );
                    $('#msg-part').removeClass( 'hide' );
                    $('#msg-ok').text(data.message);
                }	else {
                    $('#msg-error').removeClass( 'hide' );
                    $('#msg-error').text(data.message);
                }
            },error: function(data) {
                console.log(data);
            }
        });
    });
});