---
scraped_url: "https://aviationstack.com/documentation"
scraped_date: "2025-09-27"
---

# AviationStack API Documentation

## Quickstart Guide

In a rush or not interested in reading documentation? There is a short 3-Step Quickstart Guide you can use to started right away.

[Get Free API Key](https://aviationstack.com/signup/free)

## Code Examples

To get you up and running quickly, we have prepared code examples in a series of programming languages. Click below to explore.

[Code Examples](https://aviationstack.com/documentation#php)

# API Documentation

The Aviationstack API was built to provide a simple way of accessing global aviation data for real-time, historical flights, and future flights as well as allow customers to tap into an extensive data set of airline routes and other up-to-date aviation-related information. Requests to the REST API are made using a straightforward HTTP GET URL structure and responses are provided in lightweight JSON format.

The following API documentation can be applied for any major programming language and will present general integration guides and explanations around API endpoints, request parameters and response objects. If any questions remain unanswered for you, simply reach out to the aviationstack support team for assistance.

## Getting Started

### API Access Key & Authentication

After creating an aviationstack account, you will be able to retrieve your unique API access key using your account dashboard. Each aviationstack account can only be assigned one API access key.

To connect to the API, simply attach the `access_key` parameter to any valid API endpoint URL and set it to your access key. Find an example below:

```
https://api.aviationstack.com/v1/flights
    ? access_key = YOUR_ACCESS_KEY
```

**Keep your key safe:** To prevent unauthorized access to your aviationstack account, please make sure to keep your API access key safe at all times. You can always generate a new key using your account dashboard.

### 256-bit HTTPS Encryption

Available on: All Plans

Customers registered for the Aviationstack with any plans may connect to the API using industry-standard 256-bit HTTPS (SSL) encryption. You don't need a paid plan for accessing HTTPS protocol anymore.

**Example API Request:**

```
https://api.aviationstack.com
```

### API Errors

If your request to the aviationstack API does not succeed, the API will return a JSON error response that contains error `code` and `message` objects indicating the type of error that occurred. The API also supports HTTP status codes, returning a code of `200` for successful requests, and an error status code (e.g. `404`) for failed requests.

If a validation error occurs, hence, an API parameter is used in an invalid way, there will be an additional `context` object containing multiple sub-objects with the associated API parameter as the key and details about the given validation error(s) further sub-objects. Each instance of a validation error contains `key` and `message` objects.

**Example Error:**

```json
{
   "error": {
      "code": "validation_error",
      "message": "Request failed with validation error",
      "context": {
         "flight_date": [
            {
               "key": "invalid_flight_date",
               "message": "The flight date must be a valid date in the format YYYY-MM-DD."
            }
         ]
      }
   }
}
```

**Common API Errors:**

| Code | Type | Description |
| --- | --- | --- |
| `401` | `invalid_access_key` | An invalid API access key was supplied. |
| `401` | `missing_access_key` | No API access key was supplied. |
| `401` | `inactive_user` | The given user account is inactive. |
| `403` | `https_access_restricted` | HTTPS access is not supported on the current subscription plan. |
| `403` | `function_access_restricted` | The given API endpoint is not supported on the current subscription plan. |
| `404` | `invalid_api_function` | The given API endpoint does not exist. |
| `404` | `404_not_found` | Resource not found. |
| `429` | `usage_limit_reached` | The given user account has reached its monthly allowed request volume. |
| `429` | `rate_limit_reached` | The given user account has reached the rate limit. |
| `500` | `internal_error` | An internal error occurred. |

## API Endpoints

### Flights

#### Real-Time Flights
Available on: All plans

The API is capable of tracking flights and retrieving flight status information in real-time. In order to look up real-time information about one or multiple flights, you can use the API's `flights` endpoint together with optional parameters to filter your result set.

**Example API Request:**

```
https://api.aviationstack.com/v1/flights
    ? access_key = YOUR_ACCESS_KEY
```

**HTTP GET Request Parameters:**

| Object | Description |
| --- | --- |
| `access_key` | **[Required]** Your API access key, which can be found in your account dashboard. |
| `callback` | [Optional] Use this parameter to specify a JSONP callback function name to wrap your API response in. |
| `limit` | [Optional] Specify a limit of results to return in your API response. Maximum allowed value is `100` below Professional Plan and `1000` on and above Professional Plan. Default value is `100`. |
| `offset` | [Optional] Specify an offset for pagination. Example: Specifying an offset of `10` in combination with a `limit` of `10` will show results 10-20. Default offset value is `0`, starting with the first available result. |
| `flight_status` | [Optional] Filter your results by flight status. Available values: `scheduled`, `active`, `landed`, `cancelled`, `incident`, `diverted` |
| `flight_date` | [Optional] Filter your results by providing a flight date in the format `YYYY-MM-DD`. Example: `2019-02-28` |
| `dep_iata` | [Optional] Filter your results by departure city or airport using an IATA code. |
| `arr_iata` | [Optional] Filter your results by arrival city or airport using an IATA code. |
| `dep_icao` | [Optional] Filter your results by departure airport using an ICAO code. |
| `arr_icao` | [Optional] Filter your results by arrival airport using an ICAO code. |
| `airline_name` | [Optional] Filter your results by airline name. |
| `airline_iata` | [Optional] Filter your results by airline IATA code. |
| `airline_icao` | [Optional] Filter your results by airline ICAO code. |
| `flight_number` | [Optional] Filter your results by providing a flight number. Example: `2557` |
| `flight_iata` | [Optional] Filter your results by providing a flight IATA code. Example: `MU2557` |
| `flight_icao` | [Optional] Filter your results by providing a flight ICAO code. Example: `CES2557` |
| `min_delay_dep` | [Optional] Filter your results by providing a minimum amount of minutes in departure delay. Example: `7` for seven minutes of delay in departure. |
| `min_delay_arr` | [Optional] Filter your results by providing a minimum amount of minutes in arrival delay. Example: `7` for seven minutes of delay in arrival. |
| `max_delay_dep` | [Optional] Filter your results by providing a maximum amount of minutes in departure delay. Example: `60` for one hour of delay in departure. |
| `max_delay_arr` | [Optional] Filter your results by providing a maximum amount of minutes in arrival delay. Example: `60` for one hour of delay in arrival. |
| `arr_scheduled_time_arr` | [Optional] Filter your results by providing a arrival date in the format `YYYY-MM-DD`. Example: `2019-02-28` |
| `dep_scheduled_time_dep` | [Optional] Filter your results by providing a departure date in the format `YYYY-MM-DD`. Example: `2019-02-28` |

**Example API Response:**

```json
{
    "pagination": {
        "limit": 100,
        "offset": 0,
        "count": 100,
        "total": 1669022
    },
    "data": [
        {
            "flight_date": "2019-12-12",
            "flight_status": "active",
            "departure": {
                "airport": "San Francisco International",
                "timezone": "America/Los_Angeles",
                "iata": "SFO",
                "icao": "KSFO",
                "terminal": "2",
                "gate": "D11",
                "delay": 13,
                "scheduled": "2019-12-12T04:20:00+00:00",
                "estimated": "2019-12-12T04:20:00+00:00",
                "actual": "2019-12-12T04:20:13+00:00",
                "estimated_runway": "2019-12-12T04:20:13+00:00",
                "actual_runway": "2019-12-12T04:20:13+00:00"
            },
            "arrival": {
                "airport": "Dallas/Fort Worth International",
                "timezone": "America/Chicago",
                "iata": "DFW",
                "icao": "KDFW",
                "terminal": "A",
                "gate": "A22",
                "baggage": "A17",
                "delay": 0,
                "scheduled": "2019-12-12T04:20:00+00:00",
                "estimated": "2019-12-12T04:20:00+00:00",
                "actual": null,
                "estimated_runway": null,
                "actual_runway": null
            },
            "airline": {
                "name": "American Airlines",
                "iata": "AA",
                "icao": "AAL"
            },
            "flight": {
                "number": "1004",
                "iata": "AA1004",
                "icao": "AAL1004",
                "codeshared": null
            },
            "aircraft": {
                "registration": "N160AN",
                "iata": "A321",
                "icao": "A321",
                "icao24": "A0F1BB"
            },
            "live": {
                "updated": "2019-12-12T10:00:00+00:00",
                "latitude": 36.28560,
                "longitude": -106.807,
                "altitude": 12192.0,
                "direction": 114.34,
                "speed_horizontal": 894.348,
                "speed_vertical": 1.188,
                "is_ground": false
            }
        }
    ]
}
```

### Airlines

The API's `airlines` endpoint can be used to retrieve one or multiple airlines from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/airlines
    ? access_key = YOUR_ACCESS_KEY
```

### Airports

The API's `airports` endpoint can be used to retrieve one or multiple airports from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/airports
    ? access_key = YOUR_ACCESS_KEY
```

### Countries

The API's `countries` endpoint can be used to retrieve one or multiple countries from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/countries
    ? access_key = YOUR_ACCESS_KEY
```

### Cities

The API's `cities` endpoint can be used to retrieve one or multiple cities from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/cities
    ? access_key = YOUR_ACCESS_KEY
```

### Aircraft Types

The API's `aircraft_types` endpoint can be used to retrieve one or multiple aircraft types from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/aircraft_types
    ? access_key = YOUR_ACCESS_KEY
```

### Routes

The API's `routes` endpoint can be used to retrieve one or multiple flight routes from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/routes
    ? access_key = YOUR_ACCESS_KEY
```

### Taxes

The API's `taxes` endpoint can be used to retrieve one or multiple aviation taxes from the aviationstack database.

**Example API Request:**

```
https://api.aviationstack.com/v1/taxes
    ? access_key = YOUR_ACCESS_KEY
```

## Business Continuity - API Overages

Ensuring our customers achieve success is paramount to what we do at APILayer. For this reason, we will be rolling out our Business Continuity plan guaranteeing your end users will never see a drop in coverage. Every plan has a certain amount of API calls that you can make in the given month. However, we would never want to cut your traffic or impact user experience negatively for your website or application in case you get more traffic.

### What is an overage?

An overage occurs when you go over a quota for your API plan. When you reach your API calls limit, we will charge you a small amount for each new API call so we can make sure there will be no disruption in the service we provide to you and your website or application can continue running smoothly.

Prices for additional API calls will vary based on your plan. See table below for prices per call and example of an overage billing.

| Plan Name | Monthly Price | Number of Calls | Overage Price per call | Overage | Total price |
| --- | --- | --- | --- | --- | --- |
| Basic | $49.99 | 10,000 | 0.009998 | 2,000 | $69.99 |
| Professional | $149.99 | 50,000 | 0.0059996 | 10,000 | $209.99 |
| Business | $499.99 | 250,000 | 0.00399992 | 50,000 | $699.99 |

### Why does APILayer have overage fees?

Overage fees allow developers to continue using an API once a quota limit is reached and give them time to upgrade their plan based on projected future use while ensuring API providers get paid for higher usage.

### How do I know if I will be charged for overages?

When you are close to reaching your API calls limit for the month, you will receive an automatic notification (at 75%, 90% and 100% of your monthly quota). However, it is your responsibility to review and monitor for the plan's usage limitations. You are required to keep track of your quota usage to prevent overages. You can do this by tracking the number of API calls you make and checking the dashboard for up-to-date usage statistics.

### How will I be charged for my API subscription?

You will be charged for your monthly subscription plan, plus any overage fees applied. Your credit card will be billed after the billing period has ended.

### What happens if I don't have any overage fees?

In this case, there will be no change to your monthly invoice. Only billing cycles that incur overages will see any difference in monthly charges. The Business Continuity plan is an insurance plan to be used only if needed and guarantees your end users never see a drop in coverage from you.

### What if I consistently have more API calls than my plan allows?

If your site consistently surpasses the set limits each month, you may face additional charges for the excess usage. Nevertheless, as your monthly usage reaches a certain threshold, it becomes more practical to consider upgrading to the next plan. By doing so, you ensure a smoother and more accommodating experience for your growing customer base.

### I would like to upgrade my plan. How can I do that?

You can easily upgrade your plan by going to your Dashboard and selecting the new plan that would be more suitable for your business needs. Additionally, you may contact your Account Manager to discuss a custom plan if you expect a continuous increase in usage.

## Introducing Platinum Support - Enterprise-grade support for APILayer

Upgrade your APIlayer subscription with our exclusive Platinum Support, an exceptional offering designed to enhance your business' API management journey. With Platinum Support, you gain access to a host of premium features that take your support experience to a whole new level.

### What does Platinum Support include?

|  | Standard Support | Platinum Support |
| --- | --- | --- |
| General review on the issue | ✓ | ✓ |
| Access to knowledge base articles | ✓ | ✓ |
| Email support communication | ✓ | ✓ |
| Regular products updates and fixes | ✓ | ✓ |
| Dedicated account team | ✗ | ✓ |
| Priority Email Support with unlimited communication | ✗ | ✓ |
| Priority bug and review updates | ✗ | ✓ |
| Option for quarterly briefing call with product Management | ✗ | ✓ |
| Features requests as priority roadmap input into product | ✗ | ✓ |

**Priority Email Support:** Experience unrivaled responsiveness with our priority email support. Rest assured that your inquiries receive top-priority attention, ensuring swift resolutions to any issues.

**Unlimited Communication:** Communication is key, and with Platinum Support, you enjoy unlimited access to our support team. No matter how complex your challenges are, our experts are here to assist you every step of the way.

**Priority Bug Review and Fixes:** Bugs can be a headache, but not with Platinum Support. Benefit from accelerated bug review and fixes, minimizing disruptions and maximizing your API performance.

**Dedicated Account Team:** We understand the value of personalized attention. That's why Platinum Support grants you a dedicated account team, ready to cater to your specific needs and provide tailored solutions.

**Quarterly Briefing Call with Product Team:** Stay in the loop with the latest updates and insights from our Product team. Engage in a quarterly briefing call to discuss new features, enhancements, and upcoming developments.

**Priority Roadmap Input:** Your input matters! As a Platinum Support subscriber, your feature requests receive top priority, shaping our product roadmap to align with your evolving requirements.

Don't settle for the standard when you can experience the exceptional. Upgrade to Platinum Support today and supercharge your APIlayer experience!

[Upgrade now](https://aviationstack.com/product)

Read enough? Get started now by registering for a free API key!

[Get Free API Key](https://aviationstack.com/signup/free)
