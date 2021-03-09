const one = document.getElementById('first')
const two = document.getElementById('second')
const three = document.getElementById('third')
const four = document.getElementById('fourth')
const five = document.getElementById('fifth')
let i
const handler = (selection)=>{
    switch(selection){
        case 'first': {
            one.classList.add('checked')
            two.classList.remove('checked')
            three.classList.remove('checked')
            four.classList.remove('checked')
            five.classList.remove('checked')
            i = 1
            return i;
        }
        case 'second': {
            one.classList.add('checked')
            two.classList.add('checked')
            three.classList.remove('checked')
            four.classList.remove('checked')
            five.classList.remove('checked')
            i = 2
            return i;
        }
        case 'third': {
            one.classList.add('checked')
            two.classList.add('checked')
            three.classList.add('checked')
            four.classList.remove('checked')
            five.classList.remove('checked')
            i = 3
            return i;
        }
        case 'fourth': {
            one.classList.add('checked')
            two.classList.add('checked')
            three.classList.add('checked')
            four.classList.add('checked')
            five.classList.remove('checked')
            i = 4
            return i;
        }
        case 'fifth': {
            one.classList.add('checked')
            two.classList.add('checked')
            three.classList.add('checked')
            four.classList.add('checked')
            five.classList.add('checked')
            i = 5
            return i;
        }
    }
}

const arr = [one, two, three, four, five]

arr.forEach(item => item.addEventListener('mouseover', (event)=>{
    handler(event.target.id);
}))

function add_comment(product_id, content, rate){
    const data = JSON.stringify({product_id:product_id, content:content, rate:rate})
    $.ajax({
        type: "post",
        url: "{% url 'add_comment' %}",
        data: data,
        success: (response)=>{
            const resp = JSON.parse(response)
            $(`#product_comments`).prepend(`<span class="font-weight-bold">${resp['comment_user']}: </span>
                        <span >
                            {% for s in "abcde" %}
                                {% if forloop.counter <= ${resp['comment_rate']} %}
                                    <span id="rate1{{ forloop.counter }}" class="fa fa-star checked"></span>
                                {% else %}
                                    <span id="rate1{{ forloop.counter }}" class="fa fa-star "></span>
                                {% endif %}
                            {% endfor %}
                            ${resp['comment_rate']}
                        </span>
                        <script>rating({{ forloop.counter }},${resp['comment_rate']})</script>
                        <span class=""><br>${resp['comment_text']}<br></span>`)

        }
    })
}