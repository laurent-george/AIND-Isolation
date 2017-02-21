
var b;
var x;

function initGame() {
    var obj = { width : 1, height:1, player1_name:'player1', player2_name :'player2'};
      $.getJSON('http://127.0.0.1:8000/v1/game_info', function (data) {
      console.log(data);
      obj.width = data.width;
      obj.height = data.height;
      var size_str = obj.width + 'x' + obj.height;
      b = jsboard.board({ attach: "game", size: size_str });

    var piece_x = jsboard.piece({ text: "X", fontSize: "40px", textAlign: "center" });
    var piece_o = jsboard.piece({ text: "O", fontSize: "40px", textAlign: "center" });

    b.cell("each").style({width:"75px", height:"75px"});
    // alternate turns of x and o
    b.myturn = true;



    b.cell("each").on("click", function() {
    var move_coords = $(this).attr("data-matrixval").split("x")
    console.log("Move coords are" + move_coords)
    if (b.myturn)
    {





    var request = new FormData();
    request.append("move_coords", move_coords);

                jQuery.ajax({
            url: "http://localhost:8000/v1/human/move",
            type: "POST",
            crossDomain: true,
            data: JSON.stringify({move_coord : move_coords}),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            cache: false,
            success: function(resultData) {
            console.log("SUCCCESS");
            console.log(resultData)
            console.log(this)
            b.cell(resultData).place(piece_o.clone());
            b.myturn = false;
            }
    })
    }
    else
    {

                jQuery.ajax({
            url: "http://127.0.0.1:8000/v1/ia/next_move",
            type: "GET",
            async: true,
            contentType: 'application/json; charset=utf-8',
            success: function(resultData) {
            console.log(resultData)
            b.cell(resultData).place(piece_x.clone());
            b.cell("each").style({background:"lightgray"});
            b.myturn = true;


        jQuery.ajax({
            url: "http://127.0.0.1:8000/v1/human/legal_moves",
            type: "GET",
            async: true,
            contentType: 'application/json; charset=utf-8',
            success: function(resultData) {
            console.log("LEGAL MOVES ARE" + resultData)
            resultData.forEach(function(entry) {
    b.cell(entry).style({background:"lightgreen"});
});
            },
            error : function(jqXHR, textStatus, errorThrown) {
            console.log("ERROR !!!")
            },

            timeout: 240000,
        });


            },
            error : function(jqXHR, textStatus, errorThrown) {
            console.log("ERROR !!!")
            },

            timeout: 240000,
        });
        }


});

    });
    return obj;
};

initGame();
//console.log(game);


