$(document).ready(function () {
  // Set up variables

  let jwtToken = localStorage.getItem("access_token");

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Check if this cookie string begins with the name provided
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie("csrftoken");

  let sku_for_prod = document.querySelector(".card1.active").dataset.sku;
  const id_for_prod = document.getElementById("sku_for_prod").textContent;

  // Function to handle successful addition to cart for registered users
  function handleSuccess(data) {
    console.log(data);
    if (data.message_already) {
      alert(data.message_already);
      return;
    }

    if (data.name) {
      $(".cart_empt").remove();

      let cart_total_value = parseInt($(".produ_count_cart").text());
      $(".produ_count_cart").text(cart_total_value + 1);

      $(".canva_cart").addClass("show");

      $(".magariButton").on("click", () => {
        $(".canva_cart").removeClass("show");
        $(".offcanvas-backdrop").remove();
      });

      $(".for_offcanvas").append(
        `<div class="offcanvas-backdrop fade show"></div>`
      );

      $(".offcanvas-backdrop").on("click", function () {
        $(this).remove();
        $(".canva_cart").removeClass("show");
      });

      $(".off_body_forProd").append(`
          <div style="margin-bottom: 1rem;">
              <a href="${location.protocol}//${location.host}/product_detail/${data.unique_id}/" class="result_a_tag" style="display: flex;align-items: center;">
                  <img src="/static${data.img_url}" alt="" style="max-width: 70px" />
                  <span class="result-span" style="display: flex; flex-direction: column;">
                      <span style="color: black;"> ${data.name} </span>
                      <span class="price_prod" style="color: black;"> ${data.price}$ </span>
                      <span class="quantity" style="color: black;">Quantity: ${data.quantity} </span>
                  </span>
              </a>
              <div class="p-2 prod_cart_delete" style="background-color: red; cursor: pointer; text-align: center;" data-count="${data.sku}">
                  <i class="bi bi-trash text-light"></i>
              </div>
          </div>
      `);

      let sumData =
        parseFloat($(".cart_sum").text()) + parseFloat(data.total_price);
      $(".cart_sum").text(`${sumData}`);

      const prod_cart_delete = document.querySelectorAll(".prod_cart_delete");
    }
  }

  // Function to handle errors during AJAX call
  function handleError(options) {
    console.log(options.jwt_error);
    console.log(options);
    console.log(options.product);
    if (options.jwt_error == '{"error25": "Token has expired"}') {
      refreshAccessToken(options.product);
    }
  }

  // Function to refresh access token
  function refreshAccessToken(product) {
    $.ajax({
      url: `${location.protocol}//${location.host}/auth/jwt/refresh/`,
      type: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
      },
      contentType: "application/json",
      data: JSON.stringify({
        refresh: localStorage.getItem("refresh_token"),
      }),
      success: function (data) {
        console.log(data);
        localStorage.setItem("access_token", data.access);
        const jwtToken2 = localStorage.getItem("access_token");
        addToCart(jwtToken2, product);
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  }

  // Function to add to cart
  function addToCart(jwtToken, products) {
    if (!products.sku) {
      $.ajax({
        type: "POST",
        url: "/add_to_cart_users/",
        headers: {
          "X-CSRFToken": csrftoken,
          "Authorization": `Bearer ${jwtToken}`,
        },
        data: {
          "sku": products,
          "quantity": $('input[name="quantity"]').val(),
        },
        success: handleSuccess,
        error: handleError,
      });
    } else {
      $.ajax({
        type: "POST",
        url: "/add_to_cart_users/",
        headers: {
          "X-CSRFToken": csrftoken,
          "Authorization": `Bearer ${jwtToken}`,
        },
        data: {
          "sku": products.sku,
          "quantity": $('input[name="quantity"]').val(),
        },
        success: handleSuccess,
        error: handleError,
      });
    }
  }

  // handling add to cart functionality for not registered users
  function handleSuccessForNotRegistered(data) {
    console.log(data);

    if (data.message_already) {
      alert(data.message_already);
      return;
    }

    if (data.name) {
      $(".cart_empt").remove();

      let cart_total_value = parseInt($(".produ_count_cart").text());
      $(".produ_count_cart").text(cart_total_value + 1);

      $(".canva_cart").addClass("show");

      $(".magariButton").on("click", () => {
        $(".canva_cart").removeClass("show");
      });

      $(".add_new_product_div").append(`
            <div style="margin-bottom: 1rem;">
                <a href="${location.protocol}//${location.host}/product_detail/${data.unique_id}/" class="result_a_tag" style="display: flex;align-items: center;">
                    <img src="/static${data.img_url}" alt="" style="max-width: 70px" />
                    <span class="result-span" style="display: flex; flex-direction: column;">
                        <span style="color: black;"> ${data.name} </span>
                        <span class="price_prod" style="color: black;"> ${data.price}$ </span>
                        <span class="quantity" style="color: black;">Quantity: ${data.quantity} </span>
                    </span>
                </a>
                <div class="p-2 prod_cart_delete" style="background-color: red; cursor: pointer; text-align: center;" data-count="${data.sku}">
                    <i class="bi bi-trash text-light"></i>
                </div>
            </div>
        `);

      let sumData =
        parseFloat($(".cart_sum").text()) + parseFloat(data.total_price);
      $(".cart_sum").text(`${sumData}`);

      const prod_cart_delete = document.querySelectorAll(".prod_cart_delete");

      prod_cart_delete.forEach((delete_btn) => {
        delete_btn.addEventListener("click", () => {
          const skuToDelete = delete_btn.dataset.count; // Get the SKU of the product to delete
          delete_btn.parentElement.classList.add("d-none");

          let cartItems = document.cookie
            .split(";")
            .find((cookie) => cookie.trim().startsWith("cart_items="));

          if (cartItems) {
            cartItems = cartItems.split("=")[1];
            cartItems = cartItems
              .replace(/^"|"$/g, "")
              .replace(/\\054/g, ",")
              .replace(/\\/g, "")
              .replace(/'sku':\s*["']([^"']*)["']/g, '"sku": "$1"')
              .replace(/'quantity':\s*(\d+)/g, '"quantity": $1');

            let items = JSON.parse(cartItems); // Parse the JSON string into an array of objects

            // Find and remove the item with the corresponding SKU from the cart
            items = items.filter((item) => item.sku !== skuToDelete);

            // Update the cart_items cookie with the modified array
            document.cookie =
              "cart_items=" +
              JSON.stringify(items) +
              "; expires=Thu, 01 Jan 2070 00:00:00 UTC; path=/;";

            // Calculate the updated total value of items in the cart
            let cart_total_value = items.reduce(
              (total, item) => total + item.quantity,
              0
            );

            $(".cart-total").text(cart_total_value);

            // Reload the page after a short delay to reflect the changes in the cart
            setTimeout(function () {
              location.reload();
            }, 500); // Reload the page after a short delay (500 milliseconds)
          }
        });
      });
    }
  }

  function updateFilter() {
    $.ajax({
      type: "GET",
      url: "/filter_sub_products_forproduct_detail/",
      data: {
        "sku_for_prod": sku_for_prod,
      },
      success: function (response) {
        var products = response;
        let attrs = products.rec_data;

        $(".attrs_and_values").text(``);

        for (const key in attrs) {
          const element12 = attrs[key];

          $(".attrs_and_values").append(`
            
              <li class="list-group-item attr_values">
                ${key}:
                <span data-attrValue="${element12[0]}">${element12[0]}</span>
              </li> 
            
            `);
        }

        $(".name").empty();
        $(".price").empty();
        $(".description").empty();
        $(".code32").empty();
        $(".main-image").empty();
        $(".code32").text(`${products.sku.split("-")[0]}`);
        $(".price").text(`$${products.price}`);
        $(".name").text(`${products.name}`);
        $(".description").text(`${products.desc}`);
        $(".unit").text(`${products.stock}`);
        $('input[name="quantity"]').attr("max", products.stock);

        if (products.img_url == "/static/images/No Image.svg") {
          $(".defaultimg-div").append(
            `<img src="/static/images/No Image.svg" alt="">`
          );
        } else {
          $(".main-image").attr("src", `/static${products.img_url}`);
        }

        // add to cart functionality
        $(".minus")
          .off("click")
          .on("click", function () {
            let value = parseInt($('input[name="quantity"]').val());

            if (value > 1) {
              // Ensure the value is decremented by 1
              $('input[name="quantity"]').val(value - 1);
            }
          });

        $(".plus")
          .off("click")
          .on("click", function () {
            let value = parseInt($('input[name="quantity"]').val());

            if (value <= parseInt(products.stock) - 1) {
              // Ensure the value is incremented by 1
              $('input[name="quantity"]').val(value + 1);
            }
          });

        $(".add-to-cart")
          .off("click")
          .on("click", function () {
            if (products.stock == 0 || products.stock < 0) {
              alert("This product has been sold out.");
            } else {
              // these if else statement is for check if quantity is correct or not
              jwtToken = localStorage.getItem("access_token");

              // check if quantity is more than stock
              if (
                parseInt($('input[name="quantity"]').val()) >
                parseInt(products.stock)
              ) {
                $(".add-to-cart").text("Not Enough Unit");

                $(".add-to-cart").css({
                  "pointer-events": "none",
                });

                // check again

                $('input[name="quantity"]').on("input", function () {
                  if (
                    parseInt($('input[name="quantity"]').val()) >
                    parseInt(products.stock)
                  ) {
                    $(".add-to-cart").text("Not Enough Unit");

                    $(".add-to-cart").css({
                      "pointer-events": "none",
                    });
                  } else {
                    $(".add-to-cart").text("Add To Cart");

                    $(".add-to-cart").css({
                      "pointer-events": "all",
                    });
                  }
                });

                // check again
                $(".minus")
                  .off("click")
                  .on("click", function () {
                    let value = parseInt($('input[name="quantity"]').val());

                    if (value > 1) {
                      // Ensure the value is decremented by 1
                      $('input[name="quantity"]').val(value - 1);
                    }

                    if (
                      parseInt($('input[name="quantity"]').val()) >
                      parseInt(products.stock)
                    ) {
                      $(".add-to-cart").text("Not Enough Unit");

                      $(".add-to-cart").css({
                        "pointer-events": "none",
                      });
                    } else {
                      $(".add-to-cart").text("Add To Cart");

                      $(".add-to-cart").css({
                        "pointer-events": "all",
                      });
                    }
                  });
              } else if (parseInt($('input[name="quantity"]').val()) <= 0) {
                $(".add-to-cart").text("Not Enough Unit");

                $(".add-to-cart").css({
                  "pointer-events": "none",
                });

                $('input[name="quantity"]').on("input", function () {
                  if (parseInt($('input[name="quantity"]').val()) <= 0) {
                    $(".add-to-cart").text("Not Enough Unit");

                    $(".add-to-cart").css({
                      "pointer-events": "none",
                    });
                  } else {
                    $(".add-to-cart").text("Add To Cart");

                    $(".add-to-cart").css({
                      "pointer-events": "all",
                    });
                  }
                });

                $(".plus")
                  .off("click")
                  .on("click", function () {
                    let value = parseInt($('input[name="quantity"]').val());

                    if (value <= parseInt(products.stock) - 1) {
                      // Ensure the value is incremented by 1
                      $('input[name="quantity"]').val(value + 1);
                    }

                    if (parseInt($('input[name="quantity"]').val()) <= 0) {
                      $(".add-to-cart").text("Not Enough Unit");

                      $(".add-to-cart").css({
                        "pointer-events": "none",
                      });
                    } else {
                      $(".add-to-cart").text("Add To Cart");

                      $(".add-to-cart").css({
                        "pointer-events": "all",
                      });
                    }
                  });
              } else {
                if (!document.getElementById("wishproducts")) {
                  $.ajax({
                    type: "POST",
                    url: "/add_to_cart/",
                    headers: {
                      "X-CSRFToken": csrftoken,
                    },
                    data: {
                      "sku": products.sku,
                      "quantity": $('input[name="quantity"]').val(),
                    },
                    success: handleSuccessForNotRegistered,
                    error: function (xhr, status, error) {
                      console.log(error);
                      alert(xhr.responseJSON.error);
                    },
                  });
                } else {
                  $.ajax({
                    type: "POST",
                    url: "/add_to_cart_users/",
                    headers: {
                      "X-CSRFToken": csrftoken,
                      "Authorization": `Bearer ${jwtToken}`,
                    },
                    data: {
                      "sku": products.sku,
                      "quantity": $('input[name="quantity"]').val(),
                    },
                    success: handleSuccess,
                    error: function (xhr, status, error) {
                      handleError({
                        product: products.sku,
                        jwt_error: xhr.responseText,
                      });
                    },
                  });
                }
              }
            }
          });
      },
      error: function (xhr, status, error) {
        console.error(xhr.responseText);
      },
    });
  }

  const card = document.querySelectorAll(".card1");

  card.forEach((element) => {
    element.addEventListener("click", () => {
      sku_for_prod = element.dataset.sku;

      card.forEach((element5) => {
        if (element5.classList.contains("active")) {
          element5.classList.remove("active");
        }
      });

      element.classList.add("active");

      updateFilter();
    });
  });

  var mainImage = $(".main-image");
  var thumbnails = $(".thumbnail");

  // Add click event to thumbnails
  thumbnails.click(function () {
    // Change the source of the main image to the clicked thumbnail's source
    var imgSrc = $(this).attr("src");
    mainImage.attr("src", imgSrc);

    // Toggle the "active" class on the clicked thumbnail
    $(this).toggleClass("active");

    // Remove the "active" class and border from other thumbnails
    thumbnails.not(this).removeClass("active").css("border", "none");

    // Add or remove border based on the presence of the "active" class
    if ($(this).hasClass("active")) {
      $(this).css("border", "2px solid #008CBA");
    }
  });

  updateFilter();

  // rating&comment section

  let avg_rating = JSON.parse(
    document.getElementById("avg_rating").textContent
  );

  // Calculate the average rating and number of filled stars
  var averageRating = parseFloat(avg_rating);
  var numFilledStars = Math.round(averageRating);

  // Clear any existing star elements
  $(".rating-stars").empty();

  // Generate star elements and fill them based on the average rating
  for (var i = 1; i <= 5; i++) {
    var star = $("<i></i>").addClass("fas fa-star star");

    if (i > numFilledStars) {
      star.addClass("not_filled");
    }
    $(".rating-stars").append(star);
  }

  // Star rating
  $("#rating-stars").on("click", ".star", function () {
    var rating = $(this).data("value");
    $("#rating").val(rating);
    $(this).prevAll(".star").addBack().addClass("fas").removeClass("far");
    $(this).nextAll(".star").removeClass("fas").addClass("far");
  });
  // Submit review form via Ajax
  $(".rating_review_btn").on("click", () => {
    let comment = document.querySelector("#comment").value;
    let rating = document.querySelector("#rating").value;

    if (rating !== "" && comment !== "") {
      $.ajax({
        type: "POST",
        url: "/submit_review/",
        headers: {
          "X-CSRFToken": csrftoken,
          "Authorization": `Bearer ${jwtToken}`,
        },
        data: {
          "comment": comment,
          "rating": rating,
          "product_id": JSON.parse(id_for_prod),
        },
        success: function (response) {
          // Update reviews list with new review
          $("#reviews-list").prepend(
            `<li class='review-item'><p class='user-info'>
            User: <span class="user-name">${response.user}</span>
          </p><p class='rating'> Rating:
              ${response.rating}
              </p><p class='comment'> Comment:
              ${response.comment}
              </p></li>`
          );
          // Update average rating and number of ratings

          $("#average-rating").text(
            "Average Rating: " + response.average_rating.toFixed(1)
          );
          $("#num-ratings").text("Number of Ratings: " + response.num_ratings);
        },
        error: function (xhr, errmsg, err) {
          if (xhr.responseText == '{"error25": "Token has expired"}') {
            $.ajax({
              url: `${location.protocol}//${location.host}/auth/jwt/refresh/`,
              type: "POST",
              headers: {
                "X-CSRFToken": csrftoken,
              },
              contentType: "application/json",
              data: JSON.stringify({
                refresh: localStorage.getItem("refresh_token"),
              }),
              success: function (data) {
                console.log(data);
                localStorage.setItem("access_token", data.access);

                const jwtToken2 = localStorage.getItem("access_token");

                $.ajax({
                  type: "POST",
                  url: "/submit_review/",
                  headers: {
                    "X-CSRFToken": csrftoken,
                    "Authorization": `Bearer ${jwtToken2}`,
                  },
                  data: {
                    "comment": comment,
                    "rating": rating,
                    "product_id": JSON.parse(id_for_prod),
                  },
                  success: function (response) {
                    // Update reviews list with new review
                    $("#reviews-list").prepend(
                      `<li class='review-item'><p class='user-info'>
                      User: <span class="user-name">${response.user}</span>
                    </p><p class='rating'> Rating:
                        ${response.rating}
                        </p><p class='comment'> Comment:
                        ${response.comment}
                        </p></li>`
                    );
                    // Update average rating and number of ratings
                    $("#average-rating").text(
                      "Average Rating: " + response.average_rating.toFixed(1)
                    );
                    $("#num-ratings").text(
                      "Number of Ratings: " + response.num_ratings
                    );
                  },
                  error: function (xhr, errmsg, err) {
                    alert(xhr.responseJSON.error);
                  },
                });
              },
              error: function (error) {
                console.error(error);
              },
            });
          }
        },
      });
    } else {
      alert("Please Rate Product And Leave Comment");
    }
  });

  const del_comm_btn = document.querySelectorAll(".delete_comment");

  del_comm_btn.forEach((element) => {
    element.addEventListener("click", () => {
      $.ajax({
        type: "POST",
        url: "/delete_review/",
        headers: {
          "X-CSRFToken": csrftoken,
        },
        data: {
          "reviewId": element.dataset.commpk,
        },
        success: function (response) {
          if (response.status == "success") {
            // Show the alert
            $(".comment_deleted_popUp").removeClass("hide");
            $(".comment_deleted_popUp").addClass("show");

            // Set a timeout to hide the alert after 2 seconds
            setTimeout(() => {
              $(".comment_deleted_popUp").removeClass("show");
              $(".comment_deleted_popUp").addClass("hide");
            }, 2000);
          }

          $(element.parentElement).fadeOut(500, function () {
            // After the animation completes, remove the comment from the DOM
            element.parentElement.remove();
          });
        },
        error: function (xhr, errmsg, err) {
          console.log(`Error!`);
          console.log(err);
        },
      });
    });
  });
});
