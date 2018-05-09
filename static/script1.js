function buildmealParticipant(meal) {

    //let meal =  document.getElementById("mealidtext").value ;
    let parameters = {
                    mealId: meal };
    let counter = 0;
    $.getJSON("/participant", parameters , function(data,jqXHR) {
                let htmltags='<table>';
                    htmltags += "<tr>";
                    for(let index =0 ; index<data.length ; index++)
                    {

                      htmltags += "<td width='10%'><div class='art-vmenublockheader'><h3 class='t'>"+data[index].username+"</h3></div></td>";
                      counter  += 1;
                      if (counter == 8 )
                      {
                          htmltags += "</tr>";
                          counter  = 0;
                          htmltags += "<tr>";
                      }
                    }

                    if (counter<8)
                    {
                        for(let index =0 ; index<counter-1 ; index++)
                        {
                          htmltags += "<td width='10%'><div class='art-vmenublockheader'><h3 class='t'></h3></div></td>";
                        }
                          htmltags += "</tr>";
                    }
                      htmltags += "</table>";

                    document.getElementById("divParticipat"+meal).innerHTML = htmltags;

                    });
}

function buildRatingemotion() {
					var emotionsArray = ['angry','disappointed','meh', 'happy', 'inLove'];
					  $("#element").emotionsRating({
					    emotionSize: 20,
					    bgEmotion: 'meh',
					    emotions: emotionsArray,
					    color: 'gold'
					  });

						  var _gaq = _gaq || [];
					  _gaq.push(['_setAccount', 'UA-36251023-1']);
					  _gaq.push(['_setDomainName', 'jqueryscript.net']);
					  _gaq.push(['_trackPageview']);

					  (function() {
					    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
					    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
					    var s = document.getElementsByTagName('script')[0];

					    s.parentNode.insertBefore(ga, s);


					  })();

}


function dateChangeValue(value){
  document.getElementById("fisrtDate").style.visibility = "hidden";
  document.getElementById("secondDate").style.visibility = "hidden";
  document.getElementById("andlabel").style.visibility = "hidden";

  if ((value =="in") || (value =="before") || (value =="after")){
    document.getElementById("fisrtDate").style.visibility = "visible";
  }
  else if (value =="between"){
    document.getElementById("fisrtDate").style.visibility = "visible";
    document.getElementById("secondDate").style.visibility = "visible";
    document.getElementById("andlabel").style.visibility = "visible";
  }

}