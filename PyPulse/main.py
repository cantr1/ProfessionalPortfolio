# Main file for the project
import argparse
import logging
from logging import Logger
from file_functions import add_host, print_host_file, remove_host, generate_default, get_host
from async_monitor import check_target, monitor_targets
import asyncio
import aiohttp

def generate_logger() -> Logger:
    log = logging.getLogger("MyLogs")
    logging.basicConfig(filename='actions.log', level=logging.INFO,
                        format="{asctime} - {levelname} - {message}",
                        style="{",
                        datefmt="%Y-%m-%d %H:%M",)
    return log
            
def main() -> None:
    """Main function handles parsing user arguments and logging actions"""
    # Generate logger object
    logger = generate_logger()

    parser = argparse.ArgumentParser(prog="API_Project",
                                     description="A project to practice API's",
                                     epilog="Use '-h' or '--help' to view command options")
    
    parser.add_argument('-v', '--verbose', action='store_true', help='generate verbose output')
    parser.add_argument('-c', '--config', type=str, help='path to config file')
    parser.add_argument('-t', '--test', action='store_true', help='run tests against single endpoints')
    parser.add_argument('-r', '--run', action='store_true', help='run tests against all endpoints')
    parser.add_argument('-a', '--add', action='store_true', help='add endpoint to host file')
    parser.add_argument('-x', '--remove', action='store_true', help='remove endpoint from host file')
    parser.add_argument('-l', '--list', action='store_true', help='list endpoints from host file')
    parser.add_argument('-i', '--init', action='store_true', help='generate a default config file')

    args = parser.parse_args()

    # Set host file path
    config_file = args.config or "./hosts.json"

    # Process additional arguments
    if args.verbose:
        print("Verbose...")
    
    if args.list:
        print_host_file(config_file)
    
    if args.add:
        try:
            add_host(config_file)
            logging.info("Adding host to file")
        except Exception as e:
            logging.error(f"{e}")
    
    if args.remove:
        try:
            remove_host(config_file)
            logging.info("Removing host from file")
        except Exception as e:
            logging.error(f"{e}")
    
    if args.init:
        try:
            generate_default()
            logging.info("Generating default config")
        except Exception as e:
            logging.error(f"{e}")
    
    if args.test:
        try:
            host = get_host(config_file)
            async def run_test(): 
                async with aiohttp.ClientSession() as session:
                    tasks = [check_target(session, host, logger)]
                    await asyncio.gather(*tasks)
            logger.info("Starting single target test")
            asyncio.run(run_test())
            logger.info("Single test finished")
        except Exception as e:
            print(f"ERROR: {e}")
    
    if args.run:
        try:
            asyncio.run(monitor_targets(config_file, logger))
        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nNot quite what you expected, huh?")
        