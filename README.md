# 🚀 Buddy CLI

Welcome to **Buddy CLI** - your friendly command line companion powered by generative AI! 🌟

Buddy CLI is a powerful tool that helps you execute shell-related tasks, learn new concepts, and automate your workflow with ease. Whether you're a seasoned developer or just getting started, Buddy CLI is here to make your life easier.

## 🌟 Features

### Task Automation 🤖

Sometimes you have some pretty straightforward tasks that are hard to mess up, and it can be a pain memorizing the plethora of shell commands that are available - especially if you've got to chain them together. Buddy can automatically handle just about any task in your terminal by itself, if you're cool with that sort of thing, anyway.

#### Safety Guards ⚠️

If you're sane, you probably don't want these models having direct access to your system to where they can modify just about anything and potentially cause some real damage. In these cases, if you're fearful, you can ask Buddy to _carefully_ complete a task which allows you to approve every command that is potentially dangerous (so anything that isn't reading something.)

### Educational Walkthroughs 🎓

Some of us just aren't that great with command-line, and that's okay. It can be a lot to learn and keep track of, especially if you're working in different flavors of Linux or even different operating systems semi often. Luckily, Buddy has your back! 👏

By asking Buddy for help with a task, it will create a plan and walk you through executing it step-by-step. As it moves through the process with you, you are able to suggest changes and approve everything it does. As you move through each step, Buddy will provide educational context as to why each step is happening and, in the case of issues, it will help you find workaround and explain what it all means.

### Explanations

We've all read through guides and followed tutorials online where the author gives you commands to run in your shell but without the context explaining what exactly it does, or why it does it. Buddy can give you in-depth explanations of commands or command chains before you run them yourself so you can be sure you know what it's about to do - or at least learn about why it works the way it does.

### Extending Capabilities 📈

It doesn't end there. Buddy also comes with separate modules that can be enabled: **models** and **abilities**.

#### Model Support

The following LLMs are supported through Buddy:

- **OpenAI:** GPT-4, GPT-4o, GPT-4o Mini, GPT-3.5 Turbo
- **Google:** Gemini 1.5 Pro, Gemini 1.5 Flash
- **Anthropic:** Claude 3.5 Sonnet, Claude 3 Haiku

#### Abilities

Want to go even further than your own shell's capabilities? Well, Buddy is quite capable of performing more specialized tasks.

- **[TODO] Browsing:** Enable Buddy to utilize Chrome to search the web and interact with webpages for research tasks.
- **[TODO] Analysis:** Give Buddy the ability to read and understand spreadsheets, PDFs, and images.
- **[TODO] Watching:** Let Buddy watch a stream of logs for you and only tell you about what you want to know.
- **[TODO] Web Development:** Buddy can help you reason about your React or Angular app
- **[TODO] Documentation:** Ask Buddy to write that README for you _(...like this one)_
- **[TODO] Database Administration:** Allow Buddy to help you query and mutate data in MySQL, Postgres, or SQL Server
- **[TODO] Cloud:** Provision cloud resources in Azure, AWS and GCP with ease

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Docker (for isolated testing)

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/cameron5906/buddy-cli.git
   cd buddy-cli
   ```

2. Set up a virtual environment:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running Buddy CLI

To run Buddy CLI, simply use the following command:

```sh
./buddy_cli.py <command> [options]
```

For example:

```bash
./buddy_cli.py help "set up a minecraft server using Docker"
```

### Using Docker for Testing

If you want to play around with Buddy CLI without fear of something going wrong _(for it to gain your trust)_ you can run it in an isolated container based on Ubuntu 20.04.

1. Open the `sandbox` directory

   ```bash
   cd sandbox
   ```

2. Build and run the image

   ```bash
   // On Windows
   start.bat
   
   // On Linux or Mac
   chown +x ./start.sh
   ./start.sh
   ```

Within the Docker container, you can run Buddy directly:

```bash
buddy what time is it?
```

## 📚 Commands

- `buddy info` - Display usage instructions and current configuration for Buddy CLI
- `buddy <request>` - Let Buddy handle a task without any supervision _(**WARNING:** be careful!)_
- `buddy carefully <request>` - Let Buddy handle a task, but with user confirmation for every non-read action
- `buddy explain <command>` - Get detailed and informative documentation on any command(s) before you run them through your shell
- `buddy help <request>` - Let Buddy develop a plan for a task and walk you through it step-by-step, providing educational context along the way. If issues are encountered, Buddy will help you through it and make sure you know what's going on. It will even help you test & validate changes afterwards.
- `buddy use <model/ability> <name> [options]` - Enable Buddy to use a specific model or extra ability when working on tasks
- `buddy remove <model/ability>` - Removes Buddy's ability to use an ability, also removing its configuration

## 🛠 Development

Feel free to contribute to Buddy CLI! Here's how you can get started:

1. Clone the repository:

   ```sh
   git clone https://github.com/cameron5906/buddy-cli.git
   ```

2. Create a new branch:

   ```sh
   git checkout -b my-feature
   ```

3. Make your changes and commit them:

   ```sh
   git commit -m "All about my cool feature"
   ...
   ```

4. Push to the branch:

   ```sh
   git push origin my-feature-branch
   ```

5. Create a new Pull Request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🙏 Acknowledgements

- Thanks to OpenAI, Google, and Anthropic for developing some fantastic models for this use case
- Inspired by the needs of developers and those learning their way around the command-line, everywhere.
