  <div>
    <h2>Find inventories of other sellers</h2>
    <form action="" method="post">
      {{ form.hidden_tag() }}
      <p>
        {{ form.query.label }} Input a seller ID<br/>
        {{ form.query(size=32) }}<br/>
        {% for error in form.query.errors %}
        <span style="color: red;">[{{ error }}]</span>
        {% endfor %}
      </p>
      <p>{{ form.submit() }}</p>
    </form>
    <table class='table table-hover table-bordered container'>
      <thead class="thead-dark">
        <tr>
          <th scope="col">Seller ID</th>
          <th scope="col">Product ID</th>
          <th scope="col">Product Name</th>
          <th scope=""col">Image</th>
          <th scope="col">Description</th>
          <th scope="col">Quantity Remaining</th>
          <th scope="col">Unit Price</th>
          <th scope="col">Category</th>
        </tr>
      </thead>
      <tbody>
        {% for tuple in query_inventory%}
          <tr>
            <td scope="row">{{tuple.sid}}</td>
            <td scope="row">{{tuple.pid}}</td>
            <td scope="row">{{tuple.name}}</td>
            <td scope="row">{{tuple.image}}</td>
            <td scope="row">{{tuple.description}}</td>
            <td scope="row">{{tuple.quantity}}</td>
            <td scope="row">{{tuple.unit_price}}</td>
            <td scope="row">{{tuple.category}}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>