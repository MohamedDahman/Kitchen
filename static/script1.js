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

