import re
import xml.etree.ElementTree as ET
import os
from data.configuration import d4j_home, proxy_host, proxy_port, proxy_username, proxy_password

xmls = {
    'Chart': 'maven-jfreechart-project.xml',
    'Closure': 'closure-compiler.pom',
    'Codec': 'pom.xml',
    'Collections': 'pom.xml',
    'Compress': 'pom.xml',
    'Csv': 'pom.xml',
    'Gson': 'gson/pom.xml',
    'JacksonCore': 'pom.xml',
    'JacksonDatabind': 'pom.xml',
    'JacksonXml': 'pom.xml',
    'Jsoup': 'pom.xml',
    'Lang': 'pom.xml',
    'Time': 'pom.xml',
    'Math': 'pom.xml',
    'JxPath': 'project.xml',
    # 'Cli': 'project.xml',
    'Cli': 'pom.xml',
    'Mockito': 'build.gradle'
}
"{d4j_home}/framework/projects/lib/objenesis-3.3.jar"
dependency_dict = {
    "Cli": (
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/apiguardian-api-1.1.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/objenesis-3.3.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar\"></pathelement>\n"

    ),
    "Chart": (
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-api-mockito2-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-core-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/apiguardian-api-1.1.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-module-junit4-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/objenesis-3.3.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar\"></pathelement>\n"
    ),
    "Lang": (
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-api-mockito2-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-core-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/apiguardian-api-1.1.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-module-junit4-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/objenesis-3.3.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar\"></pathelement>\n"

    ),
    "Gson": (
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-api-mockito2-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-core-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/apiguardian-api-1.1.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-module-junit4-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/objenesis-3.3.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar\"></pathelement>\n"

    ),
    "Csv": (
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-api-mockito2-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-core-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/apiguardian-api-1.1.0.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/powermock-module-junit4-1.7.4.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/objenesis-3.3.jar\"></pathelement>\n"
        f"<pathelement location=\"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar\"></pathelement>\n"

    ),
}

jdk_version_dict = {
    "Cli": "1.7",
    "Chart": "1.7",
    "Lang": "1.7",
    "Gson": "1.7",
    "Csv": "1.7"
}


def parse_maven_dependencies(xml_file):
    # 解析XML文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 定义Maven命名空间
    xmlns = root.tag.split('}', 1)[0][1:]
    maven_ns = {'mvn': xmlns}

    # 查找所有的依赖项
    dependencies = root.findall('.//mvn:dependencies/mvn:dependency', namespaces=maven_ns)

    # 遍历依赖项并输出信息
    artifact_id = ''
    version = ''
    group_id = ""
    for dependency in dependencies:
        group_id = dependency.find('mvn:groupId', namespaces=maven_ns).text
        if 'junit' in group_id:
            artifact_id = dependency.find('mvn:artifactId', namespaces=maven_ns).text
            version = dependency.find('mvn:version', namespaces=maven_ns).text
            break
    return {
        'group_id': group_id,
        'artifact_id': artifact_id,
        'version': version
    }


def get_jdk_version(project):
    level = 8
    if project in ["JxPath", "Cli", "Lang"]:
        level = 3
    elif project in ["Chart", "Codec"]:
        level = 4
    elif project in ["Math", "Time", "Mockito", "Compress", "Csv", "Jsoup", "Cli"]:
        level = 5
    elif project in ["Gson", "JacksonDatabind", "Codec"]:
        level = 6
    elif project in ["JacksonCore", "JacksonXml", "JacksonDatabind", "Csv", "Jsoup"]:
        level = 7
    return level


def analyze_gradle_build(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Define regular expression patterns for extracting dependencies
    dependency_pattern = re.compile(r"['\"]?([^'\"]+):([^'\"]+):([^'\"]+)['\"]?")

    # Find all matches in the file content
    matches = re.findall(dependency_pattern, content)

    # Extracted dependencies
    dependencies = [{"group_id": match[0], "artifact_id": match[1], "version": match[2]} for match in matches]

    return dependencies


def add_dependencies(base_dir, bug_id):
    project_name = bug_id.split('_')[0]
    dependency_file_name = 'build.xml'
    # xmls[project_name]
    item_path = os.path.join(base_dir, bug_id)
    # 判断item path是否存在
    if not os.path.exists(item_path):
        print("bug_id path {} does not exit".format(item_path))
        exit(-1)

    directory_paths = [os.path.join(item_path, "fixed"), os.path.join(item_path, "buggy")]
    for fixed_directory_path in directory_paths:
        # fixed_directory_path = os.path.join(item_path, "fixed")
        if 'maven-build.xml' in os.listdir(fixed_directory_path):
            dependency_file_name = 'maven-build.xml'
        elif 'build.xml' in os.listdir(fixed_directory_path):
            dependency_file_name = 'build.xml'
        elif 'build-ant.xml' in os.listdir(fixed_directory_path):
            dependency_file_name = 'build-ant.xml'
        if 'Chart' in bug_id:
            dependency_file_name = 'ant/build.xml'
        if 'Gson' in bug_id:
            dependency_file_name = 'gson/maven-build.xml'

        dependency_file_path = os.path.join(fixed_directory_path, dependency_file_name)
        dependency_file_copy_path = dependency_file_path + ".copy"
        if not os.path.exists(dependency_file_copy_path):
            os.system("cp {} {}".format(dependency_file_path, dependency_file_copy_path))

        with open(dependency_file_copy_path, 'r') as file:
            content = file.read()
        new_content = content

        if project_name not in ['Math']:
            jdk_pattern = r"<javac(.*?)</javac>"
            existing_jdk_versions = re.findall(jdk_pattern, new_content, re.DOTALL)
            for single_jdk in existing_jdk_versions:
                target_pattern = r"target=\"(.*?)\""
                target_versions = re.findall(target_pattern, single_jdk, re.DOTALL)

                source_pattern = r"source=\"(.*?)\""
                source_versions = re.findall(source_pattern, single_jdk, re.DOTALL)

                if target_versions and source_versions:
                    target_version = target_versions[0]
                    source_version = source_versions[0]

                    if project_name in jdk_version_dict.keys():
                        new_jdk = single_jdk.replace(target_version, jdk_version_dict[project_name])
                        new_jdk = new_jdk.replace(source_version, jdk_version_dict[project_name])
                    else:
                        new_jdk = single_jdk.replace(target_version, "1.7")
                        new_jdk = new_jdk.replace(source_version, "1.7")

                    new_content = new_content.replace(single_jdk, new_jdk)
                else:
                    continue
        else:
            # 处理math的特殊情况，单独加一下classpath refid这种依赖
            math_pattern = r"<classpath>(.*?)<path refid=\"(.*?)classpath(.*?)\">(.*?)</path>(.*?)</classpath>"
            math_dependencies = re.findall(math_pattern, content, re.DOTALL)

            if len(math_dependencies) != 0:
                new_dependencies = dependency_dict[project_name] if project_name in dependency_dict.keys() else \
                dependency_dict['Chart']
                for single_dependency in math_dependencies:
                    if new_dependencies not in single_dependency[4]:
                        ori = f"<path refid=\"{single_dependency[1]}classpath{single_dependency[2]}\">{single_dependency[3]}</path>{single_dependency[4]}"
                        new_depen = single_dependency[4] + '\n' + new_dependencies
                        after = f"<path refid=\"{single_dependency[1]}classpath{single_dependency[2]}\">{single_dependency[3]}</path>{new_depen}"
                        new_content = new_content.replace(ori, after)
            pass

            config_settings = [
                proxy_host, proxy_port, proxy_username, proxy_password
            ]

            if None not in config_settings:
                proxy_settings = [
                    "<property name=\"proxy.host\" value=\"",
                    "<property name=\"proxy.port\" value=\"",
                    "<property name=\"proxy.username\" value=\"",
                    "<property name=\"proxy.password\" value=\""
                ]
                for i in range(len(proxy_settings)):
                    # 如果本来就有proxy设置
                    if proxy_settings[i] in new_content:
                        new_content = new_content.replace(proxy_settings[i], f"{proxy_settings[i]}{config_settings[i]}")
                    # 如果本来没有设置proxy，就给它加上
                    else:
                        proxy_pattern = r"<property (.*?)/>"
                        proxy_dependencies = re.findall(proxy_pattern, content, re.DOTALL)
                        if proxy_dependencies and len(proxy_dependencies) != 0:
                            ori = f"<property {proxy_dependencies[0]}/>"
                            new_content = new_content.replace(ori, f"{ori}\n{proxy_settings[i]}{config_settings[i]}\"/>\n", 1)
            else:
                pass
        pass

        pattern = r"<path id=\"(.*?)classpath(.*?)\">(.*?)</path>"

        existing_dependencies = re.findall(pattern, content, re.DOTALL)
        if len(existing_dependencies) == 0:
            if 'JxPath' in bug_id:  # ${d4j.home}
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/mockito-core-3.12.4.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/mockito-junit-jupiter-3.12.4.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/junit-jupiter-api-5.7.2.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/junit-jupiter-params-5.0.0.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/byte-buddy-1.14.11.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/byte-buddy-agent-1.14.11.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/objenesis-3.3.jar",
                                            fixed_directory_path + "/target/lib/"))
                os.system("cp {} {}".format(f"{d4j_home}/framework/projects/lib/hamcrest-2.1.jar",
                                            fixed_directory_path + "/target/lib/"))

        else:
            if 'Mockito' in bug_id:
                for single_dependency in existing_dependencies:
                    new_content = new_content.replace(single_dependency[2], single_dependency[2] + '\n' + \
                                                      f"<fileset dir=\"{d4j_home}/framework/projects/Mockito/lib\" includes=\"*.jar\" /> \n")

            else:
                new_dependencies = dependency_dict[project_name] if project_name in dependency_dict.keys() else \
                dependency_dict['Chart']
                for single_dependency in existing_dependencies:
                    if new_dependencies not in single_dependency[2]:
                        new_content = new_content.replace(single_dependency[2],
                                                          single_dependency[2] + '\n' + new_dependencies)

        with open(dependency_file_path, 'w') as file:
            file.write(new_content)


def add_dependencies_multi_proc(base_dir, bug_id, tgt_model, first_run=False):
    project_name = bug_id.split('_')[0]
    dependency_file_name = 'build.xml'
    # xmls[project_name]
    item_path = os.path.join(base_dir, bug_id + "_" + tgt_model)
    # 判断item path是否存在
    if not os.path.exists(item_path):
        print("bug_id path {} does not exit".format(item_path))
        exit(-1)
    fixed_directory_path = os.path.join(item_path, "fixed")
    buggy_directory_path = os.path.join(item_path, "buggy")
    if 'maven-build.xml' in os.listdir(fixed_directory_path):
        dependency_file_name = 'maven-build.xml'
    elif 'build.xml' in os.listdir(fixed_directory_path):
        dependency_file_name = 'build.xml'
    # else:
    #     print("build.xml and maven-build.xml both not in {}".format(fixed_directory_path))

    if 'Chart' in bug_id:
        dependency_file_name = 'ant/build.xml'
    if 'Gson' in bug_id:
        dependency_file_name = 'gson/maven-build.xml'
    # if 'Time' in bug_id:
    #     dependency_file_name = 'maven-build.xml'
    dependency_file_path = os.path.join(fixed_directory_path, dependency_file_name)
    dependency_file_copy_path = dependency_file_path + ".copy"

    # 判断是否为空
    if os.path.exists(dependency_file_path) and os.path.getsize(dependency_file_path) == 0:
        print(f'WARN: {dependency_file_path} is empty, try copy from buggy version')
        # 如果没有备份，先备份一份
        if not os.path.exists(os.path.join(buggy_directory_path, dependency_file_name) + '.backup'):
            os.system(
                f"cp -f {os.path.join(buggy_directory_path, dependency_file_name)} {os.path.join(buggy_directory_path, dependency_file_name) + '.backup'}")
        os.system(f"cp -f {os.path.join(buggy_directory_path, dependency_file_name)} {dependency_file_path}")
        if os.path.getsize(dependency_file_path) == 0:
            print(f'ERROR: file {dependency_file_path} in both buggy and fixed version are empty.')
        pass

    if first_run:
        os.system("cp -f {} {}".format(dependency_file_path, dependency_file_copy_path))

    with open(dependency_file_copy_path, 'r') as file:
        content = file.read()

    new_content = content

    pattern = r"<path id=\"(.*?).classpath\">(.*?)</path>"
    existing_dependencies = re.findall(pattern, content, re.DOTALL)
    # if project_name in ['Cli']:
    #     pattern = r"<path id=\"compile.classpath\">(.*?)</path>"
    # elif project_name in ['JacksonCore', 'JacksonDatabind', 'JacksonXml']:
    #     pattern = r"<path id=\"build.test.classpath\">(.*?)</path>"

    new_dependencies = dependency_dict[project_name] if project_name in dependency_dict.keys() else dependency_dict[
        'Chart']
    for single_dependency in existing_dependencies:
        if new_dependencies not in single_dependency[1]:
            new_content = new_content.replace(single_dependency[1], single_dependency[1] + '\n' + new_dependencies)

    jdk_pattern = r"<javac(.*?)</javac>"
    existing_jdk_versions = re.findall(jdk_pattern, new_content, re.DOTALL)
    for single_jdk in existing_jdk_versions:
        target_pattern = r"target=\"(.*?)\""
        target_versions = re.findall(target_pattern, single_jdk, re.DOTALL)

        source_pattern = r"source=\"(.*?)\""
        source_versions = re.findall(source_pattern, single_jdk, re.DOTALL)

        if target_versions and source_versions:
            target_version = target_versions[0]
            source_version = source_versions[0]
            if project_name in jdk_version_dict.keys():
                new_jdk = single_jdk.replace(target_version, jdk_version_dict[project_name])
                new_jdk = new_jdk.replace(source_version, jdk_version_dict[project_name])
            else:
                new_jdk = single_jdk.replace(target_version, "1.7")
                new_jdk = new_jdk.replace(source_version, "1.7")

            new_content = new_content.replace(single_jdk, new_jdk)
        else:
            continue

    with open(dependency_file_path, 'w') as file:
        file.write(new_content)

    # with open(os.path.join(buggy_directory_path, dependency_file_name), 'w', encoding='utf-8') as writer:
    #     writer.write(new_content)

    # # add dependencies for xml files
    # if not dependency_file_name.endswith('gradle'):
    #     pattern = r"id=build.test.classpath(.*?)</dependencies>"
    #     # Find and extract the code snippet
    #     existing_dependencies = re.findall(pattern, content, re.DOTALL)
    #     new_dependencies = """
    #                 <dependency>
    #                     <groupId>org.mockito</groupId>
    #                     <artifactId>mockito-core</artifactId>
    #                     <version>3.12.4</version>
    #                     <scope>test</scope>
    #                 </dependency>
    #         """
    #     # Add the new dependencies
    #     new_content = content.replace(existing_dependencies[0], existing_dependencies[0] + '\n' + new_dependencies)
    #     # Write the new content to the file
    #     with open(dependency_file_path, 'w') as file:
    #         file.write(new_content)


if __name__ == '__main__':
    for project in xmls:
        file = xmls[project]
        if file.endswith('.pom'):
            result = parse_maven_dependencies(file)
        elif file.endswith('.xml'):
            result = parse_maven_dependencies(file)
        else:
            result = analyze_gradle_build(file)
        print(project, result)
