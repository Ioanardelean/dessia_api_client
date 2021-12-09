# Dessia API Client
Connect your software with dessia platform instances

[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]


## Getting Started

```
pip(3) install dessia_api_client
```

## Usage

```

from dessia_api_client.users import PlatformUser

# get an api user
# replace with proper credentials
brad = PlatformUser("brad@dessia.tech", "brad_pass1!",
                  api_url="https://api.platform.dessia.tech")

# run your tests/scripts
# for eg:
all_jobs_resp = brad.jobs.list_jobs()  # list jobs
brad.jobs.submit_job(object_class="some_class", object_id=5)  # submit new one
active_apps = brad.applications.get_active_applications()  # see active apps ...


```

For interactive email/password prompt:
```
brad = PlatformUser(api_url="https://api.platform.dessia.tech")
```

See the script folder for other examples



## Issues

See the ![open issues](https://github.com/masfaraud/git_project_management/issues) for a full list of proposed features (and known issues).

## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

## License

Distributed under the LGPL License. See `LICENSE` for more information.


Project Link: [https://github.com/Dessia-tech/dessia_api_client](https://github.com/Dessia-tech/dessia_api_client)


[contributors-shield]: https://img.shields.io/github/contributors/Dessia-tech/dessia_api_client.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/Dessia-tech/dessia_api_client.svg?style=for-the-badge
[issues-shield]: https://img.shields.io/github/issues/Dessia-tech/dessia_api_client.svg?style=for-the-badge

[contributors-url]: https://github.com/Dessia-tech/dessia_api_client/graphs/contributors
[stars-url]: https://github.com/Dessia-tech/dessia_api_client/stargazers
[issues-url]: https://github.com/Dessia-tech/dessia_api_client/issues
