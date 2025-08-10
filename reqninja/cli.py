"""Command Line Interface for ReqNinja."""

import sys
import json
import click
from typing import Dict, Any, Optional
from pathlib import Path

from .client import ReqNinjaClient
from .config import Config
from .auth import parse_auth_string
from .exceptions import ReqNinjaError, ConfigError


def create_client(config_file: Optional[str] = None) -> ReqNinjaClient:
    """Create a ReqNinja client with optional config file."""
    config_path = Path(config_file) if config_file else None
    config = Config(config_path)
    return ReqNinjaClient(config)


@click.group()
@click.version_option()
@click.option('--config', '-c', help='Path to config file')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str] = None) -> None:
    """ReqNinja - HTTP client for API testing and automation."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


class HttpGroup(click.Group):
    """Custom group to provide better error messages for HTTP commands."""
    
    def get_command(self, ctx, cmd_name):
        # Try to get the command normally first
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        
        # Check if it's an uppercase method
        uppercase_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        if cmd_name in uppercase_methods:
            lowercase_method = cmd_name.lower()
            click.echo(f"❌ Use lowercase: 'reqninja http {lowercase_method}'")
            click.echo(f"📝 Example: reqninja http {lowercase_method} <url>")
            ctx.exit(1)
        
        return rv


@cli.group(cls=HttpGroup)
@click.pass_context
def http(ctx: click.Context) -> None:
    """Make HTTP requests."""
    pass


@cli.command()
@click.argument('args', nargs=-1)
@click.pass_context
def https(ctx: click.Context, args) -> None:
    """Handle https command and provide helpful guidance."""
    click.echo("❌ Use 'reqninja http' for both HTTP and HTTPS requests.")
    click.echo("📝 Examples:")
    click.echo("  reqninja http get https://api.example.com/data")
    click.echo("  reqninja http post http://localhost:3000/api/users")
    
    if args:
        method = args[0].lower() if args else ''
        url = args[1] if len(args) > 1 else ''
        if method in ['get', 'post', 'put', 'patch', 'delete'] and url:
            click.echo(f"💡 Try: reqninja http {method} {url}")
    
    ctx.exit(1)


@http.command()
@click.argument('url')
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--headers', '-H', multiple=True, help='Custom headers (key:value)')
@click.option('--auth', '-a', help='Authentication (bearer <token> | basic user:pass)')
@click.option('--timeout', '-t', type=int, help='Request timeout in seconds')
@click.option('--retries', '-r', type=int, help='Number of retries')
@click.option('--data', '-d', help='Request body data')
@click.option('--json-data', '-j', help='JSON request body')
@click.option('--raw', is_flag=True, help='Show raw response')
@click.option('--headers-only', is_flag=True, help='Show headers only')
@click.option('--save', '-s', help='Save response to file')
@click.option('--debug', is_flag=True, help='Show debug information')
@click.pass_context
def get(ctx: click.Context, **kwargs) -> None:
    """Make a GET request."""
    _make_request(ctx, 'GET', **kwargs)


@http.command()
@click.argument('url')
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--headers', '-H', multiple=True, help='Custom headers (key:value)')
@click.option('--auth', '-a', help='Authentication (bearer <token> | basic user:pass)')
@click.option('--timeout', '-t', type=int, help='Request timeout in seconds')
@click.option('--retries', '-r', type=int, help='Number of retries')
@click.option('--data', '-d', help='Request body data')
@click.option('--json-data', '-j', help='JSON request body')
@click.option('--raw', is_flag=True, help='Show raw response')
@click.option('--headers-only', is_flag=True, help='Show headers only')
@click.option('--save', '-s', help='Save response to file')
@click.option('--debug', is_flag=True, help='Show debug information')
@click.pass_context
def post(ctx: click.Context, **kwargs) -> None:
    """Make a POST request."""
    _make_request(ctx, 'POST', **kwargs)


@http.command()
@click.argument('url')
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--headers', '-H', multiple=True, help='Custom headers (key:value)')
@click.option('--auth', '-a', help='Authentication (bearer <token> | basic user:pass)')
@click.option('--timeout', '-t', type=int, help='Request timeout in seconds')
@click.option('--retries', '-r', type=int, help='Number of retries')
@click.option('--data', '-d', help='Request body data')
@click.option('--json-data', '-j', help='JSON request body')
@click.option('--raw', is_flag=True, help='Show raw response')
@click.option('--headers-only', is_flag=True, help='Show headers only')
@click.option('--save', '-s', help='Save response to file')
@click.option('--debug', is_flag=True, help='Show debug information')
@click.pass_context
def put(ctx: click.Context, **kwargs) -> None:
    """Make a PUT request."""
    _make_request(ctx, 'PUT', **kwargs)


@http.command()
@click.argument('url')
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--headers', '-H', multiple=True, help='Custom headers (key:value)')
@click.option('--auth', '-a', help='Authentication (bearer <token> | basic user:pass)')
@click.option('--timeout', '-t', type=int, help='Request timeout in seconds')
@click.option('--retries', '-r', type=int, help='Number of retries')
@click.option('--data', '-d', help='Request body data')
@click.option('--json-data', '-j', help='JSON request body')
@click.option('--raw', is_flag=True, help='Show raw response')
@click.option('--headers-only', is_flag=True, help='Show headers only')
@click.option('--save', '-s', help='Save response to file')
@click.option('--debug', is_flag=True, help='Show debug information')
@click.pass_context
def delete(ctx: click.Context, **kwargs) -> None:
    """Make a DELETE request."""
    _make_request(ctx, 'DELETE', **kwargs)


@http.command()
@click.argument('url')
@click.option('--profile', '-p', help='Configuration profile to use')
@click.option('--headers', '-H', multiple=True, help='Custom headers (key:value)')
@click.option('--auth', '-a', help='Authentication (bearer <token> | basic user:pass)')
@click.option('--timeout', '-t', type=int, help='Request timeout in seconds')
@click.option('--retries', '-r', type=int, help='Number of retries')
@click.option('--data', '-d', help='Request body data')
@click.option('--json-data', '-j', help='JSON request body')
@click.option('--raw', is_flag=True, help='Show raw response')
@click.option('--headers-only', is_flag=True, help='Show headers only')
@click.option('--save', '-s', help='Save response to file')
@click.option('--debug', is_flag=True, help='Show debug information')
@click.pass_context
def patch(ctx: click.Context, **kwargs) -> None:
    """Make a PATCH request."""
    _make_request(ctx, 'PATCH', **kwargs)


def _make_request(ctx: click.Context, method: str, **kwargs) -> None:
    """Make an HTTP request with the given parameters."""
    try:
        client = create_client(ctx.obj.get('config'))
        
        # Parse headers
        headers = {}
        for header in kwargs.get('headers', []):
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # Parse authentication
        auth_config = None
        if kwargs.get('auth'):
            auth_config = parse_auth_string(kwargs['auth'])
        
        # Prepare request data
        request_kwargs = {
            'profile': kwargs.get('profile'),
            'headers': headers if headers else None,
            'auth': auth_config,
            'timeout': kwargs.get('timeout'),
            'retries': kwargs.get('retries'),
        }
        
        # Handle request body
        if kwargs.get('data'):
            request_kwargs['data'] = kwargs['data']
        elif kwargs.get('json_data'):
            try:
                request_kwargs['json'] = json.loads(kwargs['json_data'])
            except json.JSONDecodeError as e:
                click.echo(f"Error: Invalid JSON data: {e}", err=True)
                sys.exit(1)
        
        # Check for piped input
        if not sys.stdin.isatty():
            piped_data = sys.stdin.read().strip()
            if piped_data:
                try:
                    request_kwargs['json'] = json.loads(piped_data)
                except json.JSONDecodeError:
                    request_kwargs['data'] = piped_data
        
        # Remove None values
        request_kwargs = {k: v for k, v in request_kwargs.items() if v is not None}
        
        # Make the request
        response = client.request(method, kwargs['url'], **request_kwargs)
        
        # Handle debug output
        if kwargs.get('debug'):
            _print_debug_info(response, request_kwargs)
        
        # Handle output
        if kwargs.get('save'):
            response.save(kwargs['save'])
            click.echo(f"Response saved to {kwargs['save']}")
        elif kwargs.get('raw'):
            click.echo(response.text)
        elif kwargs.get('headers_only'):
            for key, value in response.headers.items():
                click.echo(f"{key}: {value}")
        else:
            response.pretty_print(show_headers=False)
        
        # Exit with error code if request failed
        if response.status_code >= 400:
            sys.exit(1)
            
    except (ReqNinjaError, ConfigError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nRequest cancelled.", err=True)
        sys.exit(1)


def _print_debug_info(response, request_kwargs: Dict[str, Any]) -> None:
    """Print debug information."""
    click.echo("=== DEBUG INFO ===", err=True)
    click.echo(f"Request URL: {response.url}", err=True)
    click.echo(f"Request Method: {response.request.method}", err=True)
    click.echo(f"Request Headers:", err=True)
    for key, value in response.request.headers.items():
        click.echo(f"  {key}: {value}", err=True)
    
    if hasattr(response.request, 'body') and response.request.body:
        click.echo(f"Request Body: {response.request.body}", err=True)
    
    click.echo(f"Response Status: {response.status_code} {response.reason}", err=True)
    click.echo(f"Response Time: {response.elapsed_ms:.2f}ms", err=True)
    click.echo("==================", err=True)


@cli.group()
def config() -> None:
    """Manage configuration and profiles."""
    pass


@config.command('list')
@click.pass_context
def list_profiles(ctx: click.Context) -> None:
    """List available profiles."""
    try:
        client = create_client(ctx.obj.get('config'))
        profiles = client.config.list_profiles()
        
        if profiles:
            click.echo("Available profiles:")
            for profile in profiles:
                click.echo(f"  - {profile}")
        else:
            click.echo("No profiles configured.")
    except ConfigError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('show')
@click.argument('profile')
@click.pass_context
def show_profile(ctx: click.Context, profile: str) -> None:
    """Show profile configuration."""
    try:
        client = create_client(ctx.obj.get('config'))
        profile_config = client.config.get_profile(profile)
        
        click.echo(f"Profile '{profile}':")
        click.echo(json.dumps(profile_config, indent=2))
    except (ConfigError, Exception) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
