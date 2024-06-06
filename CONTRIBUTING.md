# Contributing Guidelines

*Pull requests, bug reports, and all other forms of contribution are welcomed and highly encouraged!*

### Contents

- [Code of Conduct](#code-of-conduct)
- [Opening an Issue](#opening-an-issue)
- [Feature Requests](#feature-requests)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Writing Commit Messages](#writing-commit-messages)
- [Code Review](#code-review)
- [Coding Style](#coding-style)

> **This guide serves to set clear expectations for everyone involved with the project so that we can improve it together while also creating a welcoming space for everyone to participate. Following these guidelines will help ensure a positive experience for contributors and maintainers.**

## Code of Conduct

Please note that this project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Opening an Issue

Before [creating an issue](https://help.github.com/en/github/managing-your-work-on-github/creating-an-issue), check if you are using the latest version of the project. If you are not up-to-date, see if updating fixes your issue first.

## Feature Requests

Feature requests are welcome!

- **Do not open a duplicate feature request.** Search for existing feature requests first. If you find your feature (or one very similar) previously requested, comment on that issue.

- **Fully complete the provided issue template.** The feature request template asks for all necessary information for us to begin a productive conversation. 

## Submitting Pull Requests

We **love** pull requests! Before [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests) for non-trivial changes, it is usually best to first open an issue to discuss the changes, or discuss your intended approach for solving the problem in the comments for an existing issue.

*Note: All contributions will be licensed under the project's license.*

- **Smaller is better.** Submit **one** pull request per bug fix or feature. A pull request should contain isolated changes pertaining to a single bug fix or feature implementation. It is better to **submit many small pull requests** rather than a single large one. Enormous pull requests will take enormous amounts of time to review. 

- **Use the repo's default branch.** Branch from and submit your pull request to the repo's default branch `main`.

- **[Resolve any merge conflicts](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-on-github)** that occur.

- When writing comments, use properly constructed sentences, including punctuation.

- Use spaces, not tabs.

## Branch Naming Conventions

Please use the following naming conventions for your branches:

- TicketId_feature/feature-name: For new features
- TicketId_bugfix/bugfix-name: For bug fixes
- TicketId_hotfix/hotfix-name: For critical hotfixes
- TicketId_docs/docs-change: For documentation changes
- TicketId_refactor/refactor-name: For code refactoring

Examples:

- 1_feature/add-login-page
- 1_bugfix/fix-header-typo
- 1_hotfix/security-patch
- 1_docs/update-readme
- 1_refactor/improve-api-handling


## Writing Commit Messages

Please [write a great commit message](https://chris.beams.io/posts/git-commit/). Add the subject only when a commit merits a bit of explanation and context.

1. Separate subject from body with a blank line
1. Limit the subject line to 50 characters
1. Capitalize the subject line
1. Do not end the subject line with a period
1. Use the imperative mood in the subject line (example: "Fix networking issue")
1. Use the body to explain **why**, *not what and how* (the code shows that!)
1. If applicable, prefix the title with the relevant component name. (examples: "[Docs] Fix typo", "[Profile] Fix missing avatar")

```
[TAG] Short summary of changes in 50 chars or less. For Example: "Fix typo in introduction to user guide"

Add a more detailed explanation here, if necessary. Possibly give 
some background about the issue being fixed, etc. The body of the 
commit message can be several paragraphs. Further paragraphs come 
after blank lines and please do proper word-wrap.

Wrap it to about 72 characters or so. In some contexts, 
the first line is treated as the subject of the commit and the 
rest of the text as the body. The blank line separating the summary 
from the body is critical (unless you omit the body entirely); 
various tools like `log`, `shortlog` and `rebase` can get confused 
if you run the two together.

Explain the problem that this commit is solving. Focus on why you
are making this change as opposed to how or what. The code explains 
how or what. Reviewers and your future self can read the patch, 
but might not understand why a particular solution was implemented.
Are there side effects or other unintuitive consequences of this
change? Here's the place to explain them.

 - Bullet points are okay, too

 - A hyphen or asterisk should be used for the bullet, preceded
   by a single space, with blank lines in between

Note the fixed or relevant GitHub issues at the end:

Resolves: #123
See also: #456, #789
```

## Code Review

- **Review the code.** Look for and suggest improvements. Provide actionable feedback and explain your reasoning.

- Kindly note any violations to the guidelines specified in this document. 

## Coding Style

Consistency is the most important. Following the existing style, formatting, and naming conventions of the file you are modifying and of the overall project. Failure to do so will result in a prolonged review process that has to focus on updating the superficial aspects of your code, rather than improving its functionality and performance.

For example, 

When possible, style and format will be enforced with a linter.
