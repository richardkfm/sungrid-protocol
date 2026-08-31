#!/bin/sh
# Helper script used to check and update engine dependencies
# This should not be called manually

command -v curl >/dev/null 2>&1 || command -v wget > /dev/null 2>&1 || { echo >&2 "The OpenRA mod SDK requires curl or wget."; exit 1; }
if command -v python3 >/dev/null 2>&1; then
	PYTHON="python3"
else
	command -v python >/dev/null 2>&1 || { echo >&2 "The OpenRA mod SDK requires python."; exit 1; }
	PYTHON="python"
fi

require_variables() {
	missing=""
	for i in "$@"; do
		eval check="\$$i"
		[ -z "${check}" ] && missing="${missing}   ${i}\n"
	done
	if [ ! -z "${missing}" ]; then
		echo "Required mod.config variables are missing:\n${missing}Repair your mod.config (or user.config) and try again."
		exit 1
	fi
}

TEMPLATE_LAUNCHER=$(${PYTHON} -c "import os; print(os.path.realpath('$0'))")
TEMPLATE_ROOT=$(dirname "${TEMPLATE_LAUNCHER}")

# shellcheck source=mod.config
. "${TEMPLATE_ROOT}/mod.config"

if [ -f "${TEMPLATE_ROOT}/user.config" ]; then
	# shellcheck source=user.config
	. "${TEMPLATE_ROOT}/user.config"
fi

require_variables "MOD_ID" "ENGINE_VERSION" "ENGINE_DIRECTORY"

CURRENT_ENGINE_VERSION=$(cat "${ENGINE_DIRECTORY}/VERSION" 2> /dev/null)

if [ -f "${ENGINE_DIRECTORY}/VERSION" ] && [ "${CURRENT_ENGINE_VERSION}" = "${ENGINE_VERSION}" ]; then
	exit 0
fi

if [ "${AUTOMATIC_ENGINE_MANAGEMENT}" = "True" ]; then
	require_variables "AUTOMATIC_ENGINE_SOURCE" "AUTOMATIC_ENGINE_EXTRACT_DIRECTORY" "AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME"

	echo "OpenRA engine version ${ENGINE_VERSION} is required."

	if [ -d "${ENGINE_DIRECTORY}" ]; then
		if [ "${CURRENT_ENGINE_VERSION}" != "" ]; then
			echo "Deleting engine version ${CURRENT_ENGINE_VERSION}."
		else
			echo "Deleting existing engine (unknown version)."
		fi

		rm -rf "${ENGINE_DIRECTORY}"
	fi

	echo "Downloading engine..."

	# Delete any leftover archive before starting. wget -c would otherwise try to *resume*
	# a truncated or error-page download from a previous run and never recover from it.
	rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"

	# A transient failure here used to sail straight past every check below and only surface
	# ~20 lines later as "No rule to make target 'version'", with the evidence already deleted.
	# It cost the alpha34 release its Windows installer. See docs/BACKLOG.md issue #99.
	ENGINE_DOWNLOAD_ATTEMPTS=4
	engine_download_attempt=1
	while :; do
		if command -v curl > /dev/null 2>&1; then
			# -f is the important flag: without it curl writes the HTTP error body into the
			# archive and still exits 0, so a 404 or a rate-limit page becomes "engine.zip".
			# -S keeps errors visible while -s suppresses the progress meter.
			curl -sSfL -o "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}" "${AUTOMATIC_ENGINE_SOURCE}" && break
		else
			wget -q "${AUTOMATIC_ENGINE_SOURCE}" -O "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}" && break
		fi

		rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"

		if [ "${engine_download_attempt}" -ge "${ENGINE_DOWNLOAD_ATTEMPTS}" ]; then
			echo "Failed to download the engine after ${ENGINE_DOWNLOAD_ATTEMPTS} attempts." >&2
			echo "  Source: ${AUTOMATIC_ENGINE_SOURCE}" >&2
			echo "  Check that ENGINE_VERSION in mod.config names a commit that still exists." >&2
			exit 3
		fi

		engine_download_delay=$((engine_download_attempt * 5))
		echo "Download failed (attempt ${engine_download_attempt} of ${ENGINE_DOWNLOAD_ATTEMPTS}); retrying in ${engine_download_delay}s..." >&2
		sleep "${engine_download_delay}"
		engine_download_attempt=$((engine_download_attempt + 1))
	done

	# A 2xx response still isn't proof of a usable archive, so verify before trusting it.
	if ! unzip -qqt "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}" > /dev/null 2>&1; then
		echo "The downloaded engine archive is not a valid zip file." >&2
		echo "  Source: ${AUTOMATIC_ENGINE_SOURCE}" >&2
		rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"
		exit 3
	fi

	# Github zipballs package code with a top level directory named based on the refspec
	# Extract to a temporary directory and then move the subdir to our target location
	REFNAME=$(unzip -qql "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}" | head -n1 | tr -s ' ' | cut -d' ' -f5-)
	if [ -z "${REFNAME}" ]; then
		echo "Could not determine the top level directory inside the engine archive." >&2
		rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"
		exit 3
	fi

	rm -rf "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}"
	mkdir "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}" || exit 3
	if ! unzip -qq -d "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}" "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"; then
		echo "Failed to extract the engine archive." >&2
		rm -rf "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}"
		rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"
		exit 3
	fi

	if ! mv "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}/${REFNAME}" "${ENGINE_DIRECTORY}"; then
		echo "Failed to move the extracted engine into ${ENGINE_DIRECTORY}." >&2
		rm -rf "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}"
		rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"
		exit 3
	fi

	rmdir "${AUTOMATIC_ENGINE_EXTRACT_DIRECTORY}"
	rm -f "${AUTOMATIC_ENGINE_TEMP_ARCHIVE_NAME}"

	# HACK: Remove bogus lint check that the Example mod can't possibly pass
	# because to do so it would need to define a lot of excess things surrounding resources.
	# -f because a future pinned engine may simply not carry this file; its absence was always
	# tolerated, and now that the steps around it are checked that needs saying explicitly.
	rm -f "${ENGINE_DIRECTORY}/OpenRA.Mods.Common/Lint/CheckFluentReferences.cs"

	echo "Compiling engine..."
	cd "${ENGINE_DIRECTORY}" || exit 1

	# Not exit 0: if this fails, VERSION never gets written, and reporting success would leave
	# the caller building against an engine that will be re-downloaded on the very next run.
	make version VERSION="${ENGINE_VERSION}" || exit 1
	exit 0
fi

echo "Automatic engine management is disabled."
echo "Please manually update the engine to version ${ENGINE_VERSION}."
exit 1

